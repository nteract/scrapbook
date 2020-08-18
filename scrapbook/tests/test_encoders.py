#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import mock
import pyarrow
import pandas as pd

from IPython.display import Image

from . import get_fixture_path
from ..encoders import (
    registry as full_registry,
    DataEncoderRegistry,
    JsonEncoder,
    TextEncoder,
    PandasArrowDataframeEncoder,
)
from ..exceptions import (
    ScrapbookDataException,
    ScrapbookInvalidEncoder,
    ScrapbookMissingEncoder,
)
from ..scraps import Scrap

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
        ),
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="json"),
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
        ),
        (
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="json"),
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
        ),
        (
            Scrap(name="foo", data=u'["😍"]', encoder="json"),
            Scrap(name="foo", data=["😍"], encoder="json"),
        ),
    ],
)
def test_json_decode(test_input, expected):
    assert JsonEncoder().decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input",
    [
        Scrap(name="foo", data="", encoder="json"),
        Scrap(name="foo", data='{"inavlid","json"}', encoder="json"),
        Scrap(name="foo", data="😍", encoder="json"),
    ],
)
def test_json_decode_failures(test_input):
    # If it can't decode, leaves the string as expected
    assert JsonEncoder().decode(test_input) == test_input


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
        ),
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="json"),
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
        ),
        (
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="json"),
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
        ),
        (
            Scrap(name="foo", data=u'["😍"]', encoder="json"),
            Scrap(name="foo", data=["😍"], encoder="json"),
        ),
    ],
)
def test_json_encode(test_input, expected):
    assert JsonEncoder().encode(test_input) == expected


@pytest.mark.parametrize(
    "test_input",
    [
        Scrap(name="foo", data="", encoder="json"),
        Scrap(name="foo", data='{"inavlid","json"}', encoder="json"),
        Scrap(name="foo", data="😍", encoder="json"),
    ],
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
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="text"),
            Scrap(name="foo", data=str({"foo": "bar", "baz": 1}), encoder="text"),
        ),
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="text"),
            Scrap(name="foo", data="['foo', 'bar', 1, 2, 3]", encoder="text"),
        ),
        (
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="text"),
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="text"),
        ),
        (
            Scrap(name="foo", data=Dummy(), encoder="text"),
            Scrap(name="foo", data="foo", encoder="text"),
        ),
        (Scrap(name="foo", data="😍", encoder="text"), Scrap(name="foo", data="😍", encoder="text")),
    ],
)
def test_text_decode(test_input, expected):
    assert TextEncoder().decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="text"),
            Scrap(name="foo", data=str({"foo": "bar", "baz": 1}), encoder="text"),
        ),
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="text"),
            Scrap(name="foo", data="['foo', 'bar', 1, 2, 3]", encoder="text"),
        ),
        (
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="text"),
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="text"),
        ),
        (
            Scrap(name="foo", data=Dummy(), encoder="text"),
            Scrap(name="foo", data="foo", encoder="text"),
        ),
        (Scrap(name="foo", data="😍", encoder="text"), Scrap(name="foo", data="😍", encoder="text")),
    ],
)
def test_text_encode(test_input, expected):
    assert TextEncoder().encode(test_input) == expected


@pytest.mark.parametrize(
    "test_input",
    [
        (
            Scrap(
                name="foo",
                data=pd.DataFrame(
                    data={
                        "foo": pd.Series(["bar"], dtype='str'),
                        "baz": pd.Series([1], dtype='int'),
                    }
                ),
                encoder="pandas",
            )
        ),
        (
            Scrap(
                name="foo",
                data=pd.DataFrame(
                    data={
                        "foo": pd.Series(["😍", "emoji"], dtype='str'),
                        "baz": pd.Series(["no", "unicode"], dtype='str'),
                    }
                ),
                encoder="pandas",
            )
        ),
        # Nested lists of lists of strings are ok
        (
            Scrap(
                name="foo",
                data=pd.DataFrame(data={"foo": pd.Series([[["foo", "bar"]]], dtype='object')}),
                encoder="pandas",
            )
        ),
        # String objects are ok
        (
            Scrap(
                name="foo",
                data=pd.DataFrame(data={"foo": pd.Series(["bar"], dtype='object')}),
                encoder="pandas",
            )
        ),
    ],
)
def test_pandas_encode_and_decode(test_input):
    scrap = PandasArrowDataframeEncoder().encode(test_input)
    scrap_back = PandasArrowDataframeEncoder().decode(scrap)
    pd.testing.assert_frame_equal(scrap_back.data, test_input.data)
    assert scrap.name == test_input.name
    assert scrap_back.name == test_input.name
    assert scrap.encoder == test_input.encoder
    assert scrap_back.encoder == test_input.encoder


@pytest.mark.parametrize(
    ("test_input",),
    [
        # Sets can't convert
        (
            Scrap(
                name="foo",
                data=pd.DataFrame(data={"foo": pd.Series([{"foo", "bar"}], dtype='object')}),
                encoder="pandas",
            ),
        ),
    ],
)
def test_unsupported_arrow_conversions(test_input):
    with pytest.raises(pyarrow.lib.ArrowInvalid):
        PandasArrowDataframeEncoder().encode(test_input)


@pytest.fixture
def registry():
    registry = DataEncoderRegistry()
    registry.register(JsonEncoder())
    return registry


def test_registry_register(registry):
    registry.register(TextEncoder())
    assert "text" in registry


def test_registry_invalid_register(registry):
    with pytest.raises(ScrapbookInvalidEncoder):
        registry.register("not an encoder")


def test_registry_deregister(registry):
    registry.deregister("json")
    assert "json" not in registry


def test_registry_deregister(registry):
    registry.deregister(JsonEncoder())
    assert "json" not in registry


def test_registry_missing_deregister(registry):
    with pytest.raises(KeyError):
        registry.deregister("text")


def test_registry_reset(registry):
    registry.register(TextEncoder())
    registry.reset()
    assert "json" not in registry
    assert "text" not in registry
    assert len(registry) == 0


def test_decode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.decode(Scrap(name="foo", encoder="json", data='["foobar"]')) == Scrap(
        name="foo", encoder="json", data=["foobar"]
    )


def test_encode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.encode(Scrap(name="foo", encoder="json", data='["foobar"]')) == Scrap(
        name="foo", encoder="json", data=["foobar"]
    )


class BadData(object):
    pass


class BadEncoder(object):
    def name(self):
        return "bad"

    def decode(self, scrap, **kwargs):
        return Scrap(scrap.name, data=BadData(), encoder="bad")

    def encode(self, scrap, **kwargs):
        return Scrap(scrap.name, data=BadData(), encoder="bad")


def test_bad_decode(registry):
    registry.register(BadEncoder())
    with pytest.raises(ScrapbookDataException):
        registry.decode(Scrap(name="foo", data=BadData(), encoder="bad"))


def test_bad_encode(registry):
    registry.register(BadEncoder())
    with pytest.raises(ScrapbookDataException):
        registry.encode(Scrap(name="foo", data="", encoder="bad"))


def test_missing_decode(registry):
    with pytest.raises(ScrapbookMissingEncoder):
        registry.decode(Scrap(name="foo", data="bar", encoder="missing"))


def test_missing_encode(registry):
    with pytest.raises(ScrapbookMissingEncoder):
        registry.encode(Scrap(name="foo", data="bar", encoder="missing"))


@pytest.mark.parametrize(
    "data,expected_encoder",
    [
        ("foo,bar,baz", "text"),
        (Image(filename=get_fixture_path("tiny.png")), "display"),
        (['foo', 'bar'], "json"),
        ({'foo': 'bar'}, "json"),
        (pd.DataFrame(data={"foo": pd.Series(["bar"], dtype='str')}), "pandas"),
    ],
)
def test_determine_encoder_name(data, expected_encoder):
    assert full_registry.determine_encoder_name(data) == expected_encoder


@pytest.mark.parametrize("data", [mock.Mock(), object(), TextEncoder()])
def test_determine_encoder_name_fails(data):
    with pytest.raises(NotImplementedError):
        full_registry.determine_encoder_name(data)
