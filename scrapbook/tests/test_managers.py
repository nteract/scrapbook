#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from ..managers import (
    DataManagerRegistry,
    NotebookManager,
    JsonEncoder,
    TextEncoder,
    S3ReferenceStore,
)
from ..exceptions import (
    ScrapbookException,
    ScrapbookDataException,
    ScrapbookMissingEncoder,
    ScrapbookMissingStore,
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
            Scrap(name="foo", data=[u"😍"], encoder="json"),
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
        Scrap(name="foo", data=u"😍", encoder="json"),
    ],
)
def test_json_decode_failures(test_input):
    with pytest.raises(JSONDecodeError):
        JsonEncoder().decode(test_input)


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
            Scrap(name="foo", data=[u"😍"], encoder="json"),
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
        Scrap(name="foo", data=u"😍", encoder="json"),
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
        (
            Scrap(name="foo", data=u"😍", encoder="text"),
            Scrap(name="foo", data=u"😍", encoder="text"),
        ),
    ],
)
def test_text_decode(test_input, expected):
    assert TextEncoder().decode(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="text"),
            Scrap(
                name="foo",
                data=str({"foo": "bar", "baz": 1}),
                encoder="text",
                stored_format="unicode",
            ),
        ),
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
            Scrap(
                name="foo",
                data='{"foo":"bar","baz":1}',
                encoder="text",
                stored_format="unicode",
            ),
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="text"),
            Scrap(
                name="foo",
                data="['foo', 'bar', 1, 2, 3]",
                encoder="text",
                stored_format="unicode",
            ),
        ),
        (
            Scrap(name="foo", data='["foo","bar",1,2,3]', encoder="text"),
            Scrap(
                name="foo",
                data='["foo","bar",1,2,3]',
                encoder="text",
                stored_format="unicode",
            ),
        ),
        (
            Scrap(name="foo", data=Dummy(), encoder="text"),
            Scrap(name="foo", data="foo", encoder="text", stored_format="unicode"),
        ),
        (
            Scrap(name="foo", data=u"😍", encoder="text"),
            Scrap(name="foo", data=u"😍", encoder="text", stored_format="unicode"),
        ),
        (
            Scrap(name="foo", data=u"😍", encoder="text", stored_format="utf-8"),
            Scrap(
                name="foo",
                data=u"😍".encode("utf-8"),
                encoder="text",
                stored_format="utf-8",
            ),
        ),
    ],
)
def test_text_encode(test_input, expected):
    assert TextEncoder().encode(test_input) == expected


@pytest.fixture
def registry():
    registry = DataManagerRegistry()
    registry.register("json", "notebook", NotebookManager())
    registry.register_encoder("json", NotebookManager())
    registry.register_store("notebook", NotebookManager())
    return registry


def test_registry_register(registry):
    registry.register("text", "notebook", NotebookManager())
    assert ("text", "notebook") in registry


def test_registry_register_encoder(registry):
    registry.register_encoder("text", TextEncoder())
    assert ("text", None) in registry


def test_registry_register_store(registry):
    registry.register_store("s3", S3ReferenceStore())
    assert (None, "s3") in registry


def test_registry_deregister(registry):
    registry.deregister("json", "notebook")
    assert ("json", "notebook") not in registry


def test_registry_missing_deregister(registry):
    with pytest.raises(KeyError):
        registry.deregister("text", "notebook")


def test_registry_reset(registry):
    registry.register("text", "notebook", NotebookManager())
    registry.reset()
    assert ("json", "notebook") not in registry
    assert ("text", "notebook") not in registry
    assert len(registry) == 0


def test_decode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.decode(
        Scrap(name="foo", encoder="json", store="notebook", data=["foobar"])
    ) == Scrap(name="foo", encoder="json", store="notebook", data=["foobar"])


def test_encode(registry):
    # Test that it can select and execute the qualified encoder
    assert registry.encode(
        Scrap(name="foo", encoder="json", data=["foobar"])
    ) == Scrap(name="foo", encoder="json", store="notebook", data=["foobar"])


class BadData(object):
    pass


class BadManager(object):
    def bad_data(self, scrap):
        return Scrap(scrap.name, data=BadData(), encoder="bad", store="bad")

    def bad_schema(self, scrap):
        return Scrap(scrap.name, data="")

    def encodable(self, scrap):
        return scrap.encoder == "bad"

    def storable(self, scrap):
        return scrap.store == "bad"

    def decode(self, scrap, **kwargs):
        return self.bad_data(scrap)

    def encode(self, scrap, **kwargs):
        return self.bad_data(scrap)

    def persist(self, scrap, **kwargs):
        return self.bad_data(scrap)

    def recall(self, scrap, **kwargs):
        return self.bad_data(scrap)

    def encode_and_persist(self, scrap, **kwargs):
        return self.bad_data(scrap)

    def recall_and_decode(self, scrap, **kwargs):
        return self.bad_data(scrap)


def test_bad_decode(registry):
    with pytest.raises(ScrapbookDataException):
        # Can't have data and a reference at the same time
        registry.decode(Scrap(name="foo", data="", reference="", encoder="bad", store="bad"))


def test_bad_encode(registry):
    registry.register_encoder("bad", BadManager())
    with pytest.raises(ScrapbookDataException):
        registry.encode(Scrap(name="foo", data="", encoder="bad"))


def test_bad_persist(registry):
    registry.register_store("bad", BadManager())
    with pytest.raises(ScrapbookDataException):
        registry.encode(Scrap(name="foo", data="", store="bad"))


def test_bad_encode_and_persist(registry):
    registry.register("bad", "bad", BadManager())
    with pytest.raises(ScrapbookDataException):
        registry.encode(Scrap(name="foo", data="", encoder="bad", store="bad"))


def test_missing_decode_encoder(registry):
    with pytest.raises(ScrapbookMissingEncoder):
        registry.decode(
            Scrap(name="foo", data="bar", encoder="missing", store="notebook")
        )


def test_missing_decode_store(registry):
    with pytest.raises(ScrapbookMissingStore):
        registry.decode(
            Scrap(name="foo", data="bar", encoder="json", store="missing")
        )


def test_missing_encode_encoder(registry):
    with pytest.raises(ScrapbookMissingEncoder):
        registry.encode(
            Scrap(name="foo", data="bar", encoder="missing")
        )


def test_missing_encode_store(registry):
    with pytest.raises(ScrapbookMissingStore):
        registry.encode(
            Scrap(name="foo", data="bar", store="missing")
        )
