#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from ..encoders import DataEncoderRegistry, JsonEncoder, TextEncoder
from ..exceptions import ScrapbookException, ScrapbookDataException
from ..models import Scrap

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (Scrap(data={"foo": "bar", "baz": 1}), Scrap(data={"foo": "bar", "baz": 1})),
        (Scrap(data='{"foo":"bar","baz":1}'), Scrap(data={"foo": "bar", "baz": 1})),
        (Scrap(data=["foo", "bar", 1, 2, 3]), Scrap(data=["foo", "bar", 1, 2, 3])),
        (Scrap(data='["foo","bar",1,2,3]'), Scrap(data=["foo", "bar", 1, 2, 3])),
        (Scrap(data=u'["😍"]'), Scrap(data=[u"😍"])),
    ],
)
def test_json_decode(test_input, expected):
    assert JsonEncoder().decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input", [Scrap(data=""), Scrap(data='{"inavlid","json"}'), Scrap(data=u"😍")]
)
def test_json_decode_failures(test_input):
    with pytest.raises(JSONDecodeError):
        JsonEncoder().decode(test_input)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (Scrap(data={"foo": "bar", "baz": 1}), Scrap(data={"foo": "bar", "baz": 1})),
        (Scrap(data='{"foo":"bar","baz":1}'), Scrap(data={"foo": "bar", "baz": 1})),
        (Scrap(data=["foo", "bar", 1, 2, 3]), Scrap(data=["foo", "bar", 1, 2, 3])),
        (Scrap(data='["foo","bar",1,2,3]'), Scrap(data=["foo", "bar", 1, 2, 3])),
        (Scrap(data=u'["😍"]'), Scrap(data=[u"😍"])),
    ],
)
def test_json_encode(test_input, expected):
    assert JsonEncoder().encode(test_input) == expected


@pytest.mark.parametrize(
    "test_input", [Scrap(data=""), Scrap(data='{"inavlid","json"}'), Scrap(data=u"😍")]
)
def test_json_encode_failures(test_input):
    with pytest.raises(JSONDecodeError):
        JsonEncoder().encode(test_input)


class Dummy(object):
    def __str__(self):
        return "foo"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(data={"foo": "bar", "baz": 1}),
            Scrap(data=str({"foo": "bar", "baz": 1})),
        ),
        (Scrap(data='{"foo":"bar","baz":1}'), Scrap(data='{"foo":"bar","baz":1}')),
        (Scrap(data=["foo", "bar", 1, 2, 3]), Scrap(data="['foo', 'bar', 1, 2, 3]")),
        (Scrap(data='["foo","bar",1,2,3]'), Scrap(data='["foo","bar",1,2,3]')),
        (Scrap(data=Dummy()), Scrap(data="foo")),
        (Scrap(data=u"😍"), Scrap(data=u"😍")),
    ],
)
def test_text_decode(test_input, expected):
    assert TextEncoder().decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(data={"foo": "bar", "baz": 1}),
            Scrap(data=str({"foo": "bar", "baz": 1})),
        ),
        (Scrap(data='{"foo":"bar","baz":1}'), Scrap(data='{"foo":"bar","baz":1}')),
        (Scrap(data=["foo", "bar", 1, 2, 3]), Scrap(data="['foo', 'bar', 1, 2, 3]")),
        (Scrap(data='["foo","bar",1,2,3]'), Scrap(data='["foo","bar",1,2,3]')),
        (Scrap(data=Dummy()), Scrap(data="foo")),
        (Scrap(data=u"😍"), Scrap(data=u"😍")),
    ],
)
def test_text_encode(test_input, expected):
    assert TextEncoder().encode(test_input) == expected


@pytest.fixture
def registry():
    registry = DataEncoderRegistry()
    registry.register("json", JsonEncoder())
    return registry


def test_registry_register(registry):
    registry.register("text", TextEncoder())
    assert "text" in registry


def test_registry_invalid_register(registry):
    with pytest.raises(ScrapbookException):
        registry.register("text", "not an encoder")


def test_registry_deregister(registry):
    registry.deregister("json")
    assert "json" not in registry


def test_registry_missing_deregister(registry):
    with pytest.raises(KeyError):
        registry.deregister("text")


def test_registry_reset(registry):
    registry.register("text", TextEncoder())
    registry.reset()
    assert "json" not in registry
    assert "text" not in registry
    assert len(registry) == 0


def test_decode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.decode(Scrap(encoder="json", data='["foobar"]')) == Scrap(
        encoder="json", data=["foobar"]
    )


def test_encode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.encode(Scrap(encoder="json", data='["foobar"]')) == Scrap(
        encoder="json", data=["foobar"]
    )


class BadData(object):
    pass


class BadEncoder(object):
    def decode(self, scrap, **kwargs):
        return Scrap(data=BadData())

    def encode(self, scrap, **kwargs):
        return Scrap(data=BadData())


def test_bad_decode(registry):
    with pytest.raises(ScrapbookDataException):
        registry.decode(Scrap(data=BadData()))


def test_bad_encode(registry):
    registry.register("bad", BadEncoder())
    with pytest.raises(ScrapbookDataException):
        registry.encode(Scrap(encoder="bad"))
