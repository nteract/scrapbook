#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from ..translators import DataTranslatorRegistry, JsonTranslator, UnicodeTranslator
from ..exceptions import ScrapbookException


try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"foo": "bar", "baz": 1}, {"foo": "bar", "baz": 1}),
        ('{"foo":"bar","baz":1}', {"foo": "bar", "baz": 1}),
        (["foo", "bar", 1, 2, 3], ["foo", "bar", 1, 2, 3]),
        ('["foo","bar",1,2,3]', ["foo", "bar", 1, 2, 3]),
        (u'["😍"]', [u"😍"]),
    ],
)
def test_json_load(test_input, expected):
    assert JsonTranslator().load(test_input) == expected


@pytest.mark.parametrize("test_input", [(""), ('{"inavlid","json"}'), (u"😍")])
def test_json_load_failures(test_input):
    with pytest.raises(JSONDecodeError):
        JsonTranslator().load(test_input)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"foo": "bar", "baz": 1}, {"foo": "bar", "baz": 1}),
        ('{"foo":"bar","baz":1}', {"foo": "bar", "baz": 1}),
        (["foo", "bar", 1, 2, 3], ["foo", "bar", 1, 2, 3]),
        ('["foo","bar",1,2,3]', ["foo", "bar", 1, 2, 3]),
        (u'["😍"]', [u"😍"]),
    ],
)
def test_json_translate(test_input, expected):
    assert JsonTranslator().translate(test_input) == expected


@pytest.mark.parametrize("test_input", [(""), ('{"inavlid","json"}'), (u"😍")])
def test_json_translate_failures(test_input):
    with pytest.raises(JSONDecodeError):
        JsonTranslator().translate(test_input)


class Dummy(object):
    def __str__(self):
        return "foo"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"foo": "bar", "baz": 1}, str({"foo": "bar", "baz": 1})),
        ('{"foo":"bar","baz":1}', '{"foo":"bar","baz":1}'),
        (["foo", "bar", 1, 2, 3], "['foo', 'bar', 1, 2, 3]"),
        ('["foo","bar",1,2,3]', '["foo","bar",1,2,3]'),
        (Dummy(), "foo"),
        (u"😍", u"😍"),
    ],
)
def test_unicode_load(test_input, expected):
    assert UnicodeTranslator().load(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"foo": "bar", "baz": 1}, str({"foo": "bar", "baz": 1})),
        ('{"foo":"bar","baz":1}', '{"foo":"bar","baz":1}'),
        (["foo", "bar", 1, 2, 3], "['foo', 'bar', 1, 2, 3]"),
        ('["foo","bar",1,2,3]', '["foo","bar",1,2,3]'),
        (Dummy(), "foo"),
        (u"😍", u"😍"),
    ],
)
def test_unicode_translate(test_input, expected):
    assert UnicodeTranslator().translate(test_input) == expected


@pytest.fixture
def registry():
    registry = DataTranslatorRegistry()
    registry.register("json", JsonTranslator())
    return registry


def test_registry_register(registry):
    registry.register("unicode", UnicodeTranslator())
    assert "unicode" in registry


def test_registry_invalid_register(registry):
    with pytest.raises(ScrapbookException):
        registry.register("unicode", "not a translator")


def test_registry_deregister(registry):
    registry.deregister("json")
    assert "json" not in registry


def test_registry_missing_deregister(registry):
    with pytest.raises(KeyError):
        registry.deregister("unicode")


def test_registry_reset(registry):
    registry.register("unicode", UnicodeTranslator())
    registry.reset()
    assert "json" not in registry
    assert "unicode" not in registry
    assert len(registry) == 0


def test_load_data(registry):
    # Test that it can select and execute the qualified translator
    assert registry.load_data("json", '["foobar"]') == ["foobar"]


def test_translate_data(registry):
    # Test that it can select and execute the qualified translator
    assert registry.translate_data("json", '["foobar"]') == ["foobar"]
