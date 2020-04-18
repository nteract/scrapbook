# -*- coding: utf-8 -*-
"""
encoders.py

Provides the encoders for various data types to be persistable
"""
import six
import json
import base64
import collections.abc
import pandas as pd

from io import BytesIO
from json import JSONDecodeError
from collections import OrderedDict

from .scraps import scrap_to_payload
from .exceptions import ScrapbookException, ScrapbookInvalidEncoder, ScrapbookMissingEncoder


class DataEncoderRegistry(collections.abc.MutableMapping):
    def __init__(self):
        self._encoders = OrderedDict()

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

    def register(self, encoder):
        """
        Registers a new name to a particular encoder

        Parameters
        ----------
        name: str
            Name of the mime subtype parsed by the encoder.
        encoder: obj
            The object which implements the required encoding functions.
        """
        try:
            self[encoder.name()] = encoder
        except AttributeError:
            raise ScrapbookInvalidEncoder("Encoder has no `name` method available")

    def deregister(self, encoder):
        """
        Removes a particular encoder from the registry

        Parameters
        ----------
        name: str
            Name of the mime subtype parsed by the encoder.
        """
        try:
            del self[encoder.name()]
        except AttributeError:
            del self[encoder]

    def reset(self):
        """
        Resets the registry to have no encoders.
        """
        self._encoders = {}

    def determine_encoder_name(self, data):
        """
        Determines the
        """
        for name, encoder in self._encoders.items():
            if encoder.encodable(data):
                return name
        raise NotImplementedError(
            "Scrap of type {stype} has no supported encoder registered".format(stype=type(data))
        )

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
                'No encoder found for "{data_type}" data type!'.format(data_type=encoder)
            )
        output_scrap = encoder.encode(scrap, **kwargs)
        # Run validation on encoded data
        scrap_to_payload(output_scrap)
        return output_scrap


class JsonEncoder(object):
    ENCODER_NAME = 'json'

    def name(self):
        return self.ENCODER_NAME

    def encodable(self, data):
        return isinstance(data, (list, dict, int, float, bool, str))

    def encode(self, scrap, **kwargs):
        if isinstance(scrap.data, six.string_types):
            scrap = scrap._replace(data=json.loads(scrap.data))
        return scrap

    def decode(self, scrap, **kwargs):
        # Just in case we somehow got a valid JSON string pushed
        try:
            if isinstance(scrap.data, six.string_types):
                scrap = scrap._replace(data=json.loads(scrap.data))
        except JSONDecodeError:
            # The string is an actual string and not a json string, so don't modify
            pass
        return scrap


class TextEncoder(object):
    ENCODER_NAME = 'text'

    def name(self):
        return self.ENCODER_NAME

    def encodable(self, data):
        return isinstance(data, str)

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


class DisplayEncoder(object):
    ENCODER_NAME = 'display'

    def name(self):
        return self.ENCODER_NAME

    def encodable(self, data):
        from IPython.display import DisplayObject

        return isinstance(data, DisplayObject)

    def encode(self, scrap, **kwargs):
        raise NotImplementedError("This code path should not be reached")

    def decode(self, scrap, **kwargs):
        raise NotImplementedError("This code path should not be reached")


class PandasArrowDataframeEncoder(object):
    ENCODER_NAME = 'pandas'

    def name(self):
        return self.ENCODER_NAME

    def encodable(self, data):
        return isinstance(data, pd.DataFrame)

    def encode(self, scrap, **kwargs):
        scrap_bytes = BytesIO()
        scrap.data.to_parquet(scrap_bytes, engine="pyarrow", **kwargs)
        scrap_bytes.seek(0)
        return scrap._replace(data=base64.b64encode(scrap_bytes.getvalue()).decode())

    def decode(self, scrap, **kwargs):
        scrap_bytes = BytesIO(base64.b64decode(scrap.data))
        scrap_bytes.seek(0)
        return scrap._replace(data=pd.read_parquet(scrap_bytes, engine="pyarrow", **kwargs))


registry = DataEncoderRegistry()
# Ordering here matters!
registry.register(TextEncoder())
registry.register(JsonEncoder())
registry.register(DisplayEncoder())
registry.register(PandasArrowDataframeEncoder())
