# -*- coding: utf-8 -*-
"""
managers.py

Provides the encoders and stores for various data types to be persisted / recalled
"""
import six
import json
import retry
import pandas as pd
import collections

from io import BytesIO
from collections import OrderedDict

# We lean on papermill's readers to connect to remote stores
from papermill.iorw import S3
from papermill.exceptions import PapermillRateLimitException

from .scraps import scrap_to_payload
from .exceptions import (
    ScrapbookException,
    ScrapbookMissingEncoder,
    ScrapbookMissingStore,
)


class DataManagerRegistry(collections.MutableMapping):
    def __init__(self):
        self._managers = OrderedDict()

    def __getitem__(self, key):
        return self._managers.__getitem__(key)

    def __setitem__(self, key, value):
        return self._managers.__setitem__(key, value)

    def __delitem__(self, key):
        return self._managers.__delitem__(key)

    def __iter__(self):
        return self._managers.__iter__()

    def __len__(self):
        return self._managers.__len__()

    def register(self, encoder_name, store_name, manager):
        """
        Registers a new name to a particular encoder

        Parameters
        ----------
        encoder_name: str (or None)
            Name of the mime subtype parsed by the encoder. None implies any.
        store_name: str (or None)
            The specific storage type that this encoder supports. None implies any.
        encoder: obj
            The object which implements the required encoding functions.
        """
        # Add the registered name so we can reverse look-up these fields
        manager.encoder_name = encoder_name
        manager.store_name = store_name
        self[(encoder_name, store_name)] = manager

    def register_encoder(self, name, encoder):
        self.register(name, None, encoder)

    def register_store(self, name, store):
        self.register(None, name, store)

    def deregister(self, encoder_name, store_name):
        """
        Removes a particular encoder from the registry

        Parameters
        ----------
        name: str
            Name of the mime subtype parsed by the encoder.
        store: str (optional)
            The specific storage type that this encoder supports.
        """
        del self[(encoder_name, store_name)]

    def reset(self):
        """
        Resets the registry to have no encoders.
        """
        self._managers = OrderedDict()

    def find_manager(self, scrap):
        if scrap.encoder is not None and scrap.store is not None:
            return self.get((scrap.encoder, scrap.store))

        for manager in reversed(list(self.values())):
            # Only check for managers here that can both encode and store
            if not (manager.encoder_name and manager.store_name):
                continue
            try:
                # Find matches both the encoder and the store are valid for the
                # constraints the scrap provides
                if ((scrap.encoder == manager.encoder_name or
                    (scrap.encoder is None and manager.encodable(scrap))
                ) and (scrap.store == manager.store_name or
                    (scrap.store is None and manager.storable(scrap))
                )):
                    return manager
            except AttributeError:
                # Skip any manager that don't implement encoding and storage
                pass

    def find_encoder(self, scrap):
        """
        Searches for encoders in order of registration that can encode a given
        scap.

        Parameters
        ----------
        scrap: Scrap
            A partially filled in scrap with data that needs decoding
        """
        if scrap.encoder is not None:
            return self.get((scrap.encoder, None))

        for encoder in reversed(list(self.values())):
            try:
                # Only look for stand-alone encoders, not encoders + stores
                if encoder.store_name is None and encoder.encodable(scrap):
                    return encoder
            except AttributeError:
                # Skip any encoders that don't implement discovery
                pass

    def find_store(self, scrap):
        """
        Searches for store in order of registration that can read a given
        scap reference independent of encoder.

        Parameters
        ----------
        scrap: Scrap
            A partially filled in scrap with the ref that needs persistance
        """
        if scrap.store is not None:
            return self.get((None, scrap.store))

        # Let stores match more complicated refs, like full s3 paths
        for store in reversed(list(self.values())):
            try:
                # Only look for stand-alone stores, not encoders + stores
                if store.encoder_name is None and store.storable(scrap):
                    return store
            except AttributeError:
                # Skip any stores that don't implement discovery
                pass

    def fetch_encoder_and_store(self, scrap):
        encoder = self.find_encoder(scrap)
        if not encoder:
            raise ScrapbookMissingEncoder(
                'No encoder found for "{encoder}" encoder type!'.format(
                    encoder=scrap.encoder
                )
            )
        # Find raw data fetcher
        store = self.find_store(scrap)
        if not store:
            raise ScrapbookMissingStore(
                'No store found for "{store}" store at "{ref}" reference!'.format(
                    store=scrap.store, ref=scrap.reference
                )
            )
        return encoder, store

    def decode(self, scrap, **kwargs):
        """
        Finds the register for the given encoder and translates the scrap's data
        from a string or JSON type to an object of the encoder output type.

        Parameters
        ----------
        scrap: Scrap
            A partially filled in scrap with data that needs decoding
        """
        # Run validation on encoded data
        scrap_to_payload(scrap)
        manager = self.find_manager(scrap)
        if manager:
            output_scrap = manager.recall_and_decode(scrap, **kwargs)
            output_scrap = output_scrap._replace(
                encoder=manager.encoder_name, store=manager.store_name
            )
        else:
            encoder, store = self.fetch_encoder_and_store(scrap)
            output_scrap = store.recall(scrap, **kwargs)
            output_scrap = loader.decode(output_scrap, **kwargs)
            output_scrap = output_scrap._replace(
                encoder=encoder.encoder_name, store=store.store_name
            )
        return output_scrap

    def encode(self, scrap, **kwargs):
        """
        Finds the register for the given encoder and translates the scrap's data
        from an object of the encoder type to a JSON typed object.

        Parameters
        ----------
        scrap: Scrap
            A partially filled in scrap with data that needs encoding
        """
        manager = self.find_manager(scrap)
        if manager:
            output_scrap = manager.encode_and_persist(scrap, **kwargs)
            output_scrap = output_scrap._replace(
                encoder=manager.encoder_name, store=manager.store_name
            )
        else:
            encoder, store = self.fetch_encoder_and_store(scrap)
            output_scrap = encoder.encode(scrap, **kwargs)
            output_scrap = store.persist(output_scrap, **kwargs)
            output_scrap = output_scrap._replace(
                encoder=encoder.encoder_name, store=store.store_name
            )

        # Run validation on encoded data
        scrap_to_payload(output_scrap)
        return output_scrap


class JsonEncoder(object):
    def encodable(self, scrap):
        # Only check the top object as it's expensive to do a json.dumps
        return isinstance(scrap.data, (list, dict))

    def encode(self, scrap, **kwargs):
        if isinstance(scrap.data, six.string_types):
            scrap = scrap._replace(data=json.loads(scrap.data))
        return scrap

    def decode(self, scrap, **kwargs):
        # Just in case we somehow got a valid JSON string pushed
        if isinstance(scrap.data, six.string_types):
            scrap = scrap._replace(data=json.loads(scrap.data))
        return scrap


class TextEncoder(object):
    def encodable(self, scrap):
        return isinstance(scrap.data, six.string_types)

    def encode(self, scrap, encoding=None, **kwargs):
        if not isinstance(scrap.data, six.string_types):
            scrap = scrap._replace(data=str(scrap.data))
        if encoding is not None:
            scrap = scrap._replace(stored_format=encoding)

        if scrap.stored_format is not None and scrap.stored_format != "unicode":
            scrap = scrap._replace(data=scrap.data.encode(scrap.stored_format))
        else:
            scrap = scrap._replace(stored_format="unicode")
        return scrap

    def decode(self, scrap, **kwargs):
        # Just in case we somehow got a non-string saved?!
        if not isinstance(scrap.data, six.string_types):
            scrap = scrap._replace(data=str(scrap.data))
        if scrap.stored_format is not None and scrap.stored_format != "unicode":
            scrap = scrap._replace(data=scrap.data.decode(scrap.stored_format))
        return scrap


class PandasArrowDataframeEncoder(object):
    def encodable(self, scrap):
        return isinstance(scrap.data, pd.DataFrame)

    def encode(self, scrap, **kwargs):
        scrap_bytes = BytesIO()
        scrap.data.to_parquet(scrap_bytes, engine="pyarrow", **kwargs)
        scrap_bytes.seek(0)
        return scrap._replace(data=scrap_bytes.getvalue())

    def decode(self, scrap, **kwargs):
        scrap_bytes = BytesIO(scrap.data)
        return scrap._replace(
            data=pd.read_parquet(scrap_bytes, engine="pyarrow", **kwargs)
        )


class StorageFormatAware(object):
    def stored_as_format(self, scrap, warpped_format):
        return scrap.stored_format and scrap.stored_format.endswith(warpped_format)

    def append_store_format(self, scrap, warpped_format):
        if scrap.stored_format:
            return scrap._replace(
                stored_format="{}:{}".format(scrap.stored_format, warpped_format)
            )
        else:
            return scrap._replace(stored_format=warpped_format)

    def strip_store_format(self, scrap, warpped_format):
        if scrap.stored_format.endswith(":" + warpped_format):
            scrap = scrap._replace(stored_format=scrap.stored_format.rsplit(":", 1)[0])
        elif scrap.stored_format.endswith(warpped_format):
            scrap = scrap._replace(stored_format=None)
        return scrap


# We have to extend papermill's S3 wrapper here for handling bytes
class ByteExtendedS3(S3):
    def cp_bytes(self, source, dest, **kwargs):
        """
        Copies source string into the destination location.

        Parameters
        ----------
        source: bytes
            the bytes with the content to copy
        dest: string
            the s3 location
        """

        assert isinstance(source, bytes), "source must be bytes"
        assert self._is_s3(dest), "Destination must be s3 location"

        return self._put_bytes(source, dest, **kwargs)

    def _put_bytes(
        self,
        source,
        dest,
        num_callbacks=10,
        policy="bucket-owner-full-control",
        **kwargs
    ):
        key = self._get_key(dest)
        obj = self.s3.Object(key.bucket.name, key.name)
        obj.put_object(Body=source, ACL=policy)
        return key

    def read_bytes_file(self, source, compressed=False):
        """
        Iterates over a file in s3

        Returns the full contents.

        """
        buffers = []
        for block in self.cat(source, compressed=compressed, encoding=None, raw=True):
            buffers.append(block)

        return b"".join(buffers)

    def read_string_file(self, source, compressed=False):
        """
        Iterates over a file in s3

        Returns the full contents.

        """
        buffers = []
        for block in self.cat(source, compressed=compressed, encoding="UTF-8"):
            buffers.append(block)

        return "".join(buffers)


class S3ReferenceStore(object):
    def storable(self, scrap):
        return scrap.ref and scrap.ref.startswith("s3")

    def persist(self, scrap, **kwargs):
        if isinstance(scrap.data, bytes):
            ByteExtendedS3().cp_bytes(scrap.data, scrap.ref)
            scrap = self.append_store_format(scrap, "binary")
        else:
            ByteExtendedS3().cp_string(scrap.data, scrap.ref)
        return scrap._replace(data=None)

    def recall(self, scrap, **kwargs):
        if self.stored_as_format(scrap, "binary"):
            scrap = scrap._replace(data=ByteExtendedS3().read_bytes_file(path))
            scrap = self.strip_store_format(scrap, "binary")
        else:
            scrap = scrap._replace(data=ByteExtendedS3().read_string_file(path))
        return scrap


class NotebookManager(StorageFormatAware):
    """
    Manages data saved directly in notebook outputs.
    """

    def encodable(self, scrap):
        # Only check the top object as it's expensive to do a json.dumps
        return isinstance(scrap.data, tuple([list, dict] + list(six.string_types)))

    def encode(self, scrap, **kwargs):
        return scrap

    def decode(self, scrap, **kwargs):
        return scrap

    def storable(self, scrap):
        return True

    def convert_data_from_base64(self, scrap):
        return scrap._replace(data=base64.b64decode(scrap.data.encode()))

    def convert_data_to_base64(self, scrap):
        return scrap._replace(data=base64.b64encode(scrap.data).decode())

    def persist(self, scrap, **kwargs):
        if isinstance(scrap.data, bytes):
            scrap = self.convert_data_to_base64(scrap)
            scrap = self.append_store_format(scrap, "base64")
        return scrap

    def recall(self, scrap, **kwargs):
        if self.stored_as_format(scrap, "base64"):
            scrap = self.convert_data_from_base64(scrap)
            scrap = self.strip_store_format(scrap, "base64")
        return scrap

    def encode_and_persist(self, scrap, **kwargs):
        return self.persist(self.encode(scrap, **kwargs), **kwargs)

    def recall_and_decode(self, scrap, **kwargs):
        return self.decode(self.recall(scrap, **kwargs), **kwargs)


registry = DataManagerRegistry()
# This has to be registered first to ensure lookup ordering
registry.register("json", "notebook", NotebookManager())
registry.register_store("notebook", NotebookManager())

registry.register_encoder("text", TextEncoder())
registry.register_encoder("json", JsonEncoder())
registry.register_encoder("arrow", PandasArrowDataframeEncoder())

registry.register_store("s3", S3ReferenceStore())
