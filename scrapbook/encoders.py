# -*- coding: utf-8 -*-
"""
encoders.py

Provides the encoders for various data types to be persistable
"""
import six
import json
import collections

from .scraps import scrap_to_payload
from .exceptions import ScrapbookException, ScrapbookMissingEncoder


class DataEncoderRegistry(collections.MutableMapping):
    def __init__(self):
        self._encoders = {}

    def __getitem__(self, key):
        return self._encoders.__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(value, six.string_types) or not (
            getattr(value, "encode", None) and callable(value.encode)
        ):
            raise ScrapbookException("Can't register object without 'encode' method.")
        if isinstance(value, six.string_types) or not (
            getattr(value, "decode", None) and callable(value.decode)
        ):
            raise ScrapbookException("Can't register object without 'decode' method.")

        return self._encoders.__setitem__(key, value)

    def __delitem__(self, key):
        return self._encoders.__delitem__(key)

    def __iter__(self):
        return self._encoders.__iter__()

    def __len__(self):
        return self._encoders.__len__()

    def register(self, name, encoder):
        """
        Registers a new name to a particular encoder

        Parameters
        ----------
        name: str
            Name of the mime subtype parsed by the encoder.
        encoder: obj
            The object which implements the required encoding functions.
        """
        # TODO: Make the translators specify what types they can store?
        self[name] = encoder

    def deregister(self, name):
        """
        Removes a particular encoder from the registry

        Parameters
        ----------
        name: str
            Name of the mime subtype parsed by the encoder.
        """
        del self[name]

    def reset(self):
        """
        Resets the registry to have no encoders.
        """
        self._encoders = {}

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
        loader = self._encoders.get(scrap.encoder)
        if not loader:
            raise ScrapbookMissingEncoder(
                'No encoder found for "{}" encoder type!'.format(scrap.encoder)
            )
        return loader.decode(scrap, **kwargs)

    def encode(self, scrap, **kwargs):
        """
        Finds the register for the given encoder and translates the scrap's data
        from an object of the encoder type to a JSON typed object.

        Parameters
        ----------
        scrap: Scrap
            A partially filled in scrap with data that needs encoding
        """
        encoder = self._encoders.get(scrap.encoder)
        if not encoder:
            raise ScrapbookMissingEncoder(
                'No encoder found for "{data_type}" data type!'.format(
                    data_type=encoder
                )
            )
        output_scrap = encoder.encode(scrap, **kwargs)
        # Run validation on encoded data
        scrap_to_payload(output_scrap)
        return output_scrap


class JsonEncoder(object):
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
    def encode(self, scrap, **kwargs):
        if not isinstance(scrap.data, six.string_types):
            # TODO: set encoder information to save as encoding
            scrap = scrap._replace(data=str(scrap.data))
        return scrap

    def decode(self, scrap, **kwargs):
        # Just in case we somehow got a non-string saved?!
        if not isinstance(scrap.data, six.string_types):
            # TODO: read from encoder information to load as encoding
            scrap = scrap._replace(data=str(scrap.data))
        return scrap


class ArrowDataframeEncoder(object):
    def encode(self, scrap, **kwargs):
        raise NotImplementedError("Implement eventually")

    def decode(self, scrap, **kwargs):
        raise NotImplementedError("Implement eventually")


registry = DataEncoderRegistry()
registry.register("text", TextEncoder())
registry.register("json", JsonEncoder())
# registry.register('arrow', ArrowDataframeEncoder())
