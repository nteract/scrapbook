# -*- coding: utf-8 -*-
"""
notebook.py

Provides the translators for various data types to be persistable
"""
import six
import json
import collections

from .exceptions import ScrapbookException


class DataTranslatorRegistry(collections.MutableMapping):
    def __init__(self):
        self._translators = {}

    def __getitem__(self, key):
        return self._translators.__getitem__(key)

    def __setitem__(self, key, value):
        if not (getattr(value, "translate", None) and callable(value.translate)):
            raise ScrapbookException(
                "Can't register object without 'translate' method."
            )
        if not (getattr(value, "load", None) and callable(value.translate)):
            raise ScrapbookException("Can't register object without 'load' method.")
        return self._translators.__setitem__(key, value)

    def __delitem__(self, key):
        return self._translators.__delitem__(key)

    def __iter__(self):
        return self._translators.__iter__()

    def __len__(self):
        return self._translators.__len__()

    def register(self, storage_type, translator):
        """
        Registers a new storage_type to a particular translator

        Parameters
        ----------
        storage_type: str
            Name of the mime subtype parsed by the translator.
        translator: obj
            The object which implements the required functions.
        """
        # TODO: Make the translators specify what types they can store?
        self[storage_type] = translator

    def deregister(self, storage_type):
        """
        Removes a particular translator from the registry

        Parameters
        ----------
        storage_type: str
            Name of the mime subtype parsed by the translator.
        """
        del self[storage_type]

    def reset(self):
        """
        Resets the registry to have no translators.
        """
        self._translators = {}

    # TODO: Add name
    def load_data(self, storage_type, scrap):
        """
        Finds the register for the given storage_type and loads the scrap into
        a JSON or string object.

        Parameters
        ----------
        storage_type: str
            Name of the mime subtype parsed by the translator.
        scrap: obj
            Object to be converted from JSON or string format to the original value.
        """
        loader = self._translators.get(storage_type)
        if not loader:
            raise ScrapbookException(
                'No translator found for "{}" data type!'.format(storage_type)
            )
        return loader.load(scrap)

    # TODO: Add name
    def translate_data(self, storage_type, scrap):
        """
        Finds the register for the given storage_type and translates the scrap into
        an object of the translator output type.

        Parameters
        ----------
        storage_type: str
            Name of the mime subtype parsed by the translator.
        scrap: obj
            Object to be converted to JSON or string format for storage in an output
        """
        translator = self._translators.get(storage_type)
        if not translator:
            raise ScrapbookException(
                'No translator found for "{}" data type!'.format(storage_type)
            )
        return translator.translate(scrap)


class JsonTranslator(object):
    def translate(self, scrap):
        if isinstance(scrap, six.string_types):
            return json.loads(scrap)
        return scrap

    def load(self, scrap):
        # Just in case we somehow got a valid JSON string pushed
        if isinstance(scrap, six.string_types):
            return json.loads(scrap)
        return scrap


class UnicodeTranslator(object):
    def translate(self, scrap):
        if not isinstance(scrap, six.string_types):
            return str(scrap)
        return scrap

    def load(self, scrap):
        # Just in case we somehow got a non-string saved?!
        if not isinstance(scrap, six.string_types):
            return str(scrap)
        return scrap


class ArrowDataframeTranslator(object):
    def translate(self, scrap):
        pass  # TODO: Implement

    def load(self, scrap):
        pass  # TODO: Implement


registry = DataTranslatorRegistry()
registry.register("unicode", UnicodeTranslator())
registry.register("json", JsonTranslator())
# registry.register('arrow', ArrowDataframeTranslator())
