#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import base64
import pytest

from ..scraps import Scrap, scrap_to_payload, payload_to_scrap
from ..schemas import LATEST_SCRAP_VERSION
from ..exceptions import ScrapbookDataException


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(
                name="foo",
                data='{"foo":"bar","baz":1}',
                encoder="text",
                store="notebook",
            ),
            {
                "name": "foo",
                "data": '{"foo":"bar","baz":1}',
                "encoder": "text",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(
                name="foo",
                data=base64.b64encode(u"😍".encode("utf-8")).decode(),
                encoder="text",
                store="notebook",
                stored_format="utf-8:base64",
            ),
            {
                "name": "foo",
                "data": "8J+YjQ==",
                "encoder": "text",
                "store": "notebook",
                "stored_format": "utf-8:base64",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(
                name="foo",
                data={"foo": "bar", "baz": 1},
                encoder="json",
                store="notebook",
            ),
            {
                "name": "foo",
                "data": {"foo": "bar", "baz": 1},
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(
                name="foo",
                data=["foo", "bar", 1, 2, 3],
                encoder="json",
                store="notebook",
            ),
            {
                "name": "foo",
                "data": ["foo", "bar", 1, 2, 3],
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(name="foo", data=[u"😍"], encoder="json", store="notebook"),
            {
                "name": "foo",
                "data": [u"😍"],
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(
                name="foo", reference="s3://foo/bar.json", encoder="json", store="s3"
            ),
            {
                "name": "foo",
                "reference": "s3://foo/bar.json",
                "encoder": "json",
                "store": "s3",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
    ],
)
def test_scrap_to_payload(test_input, expected):
    assert scrap_to_payload(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            {
                "name": "foo",
                "data": '{"foo":"bar","baz":1}',
                "encoder": "text",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(
                name="foo",
                data='{"foo":"bar","baz":1}',
                encoder="text",
                store="notebook",
            ),
        ),
        (
            {
                "name": "foo",
                "data": {"foo": "bar", "baz": 1},
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(
                name="foo",
                data={"foo": "bar", "baz": 1},
                encoder="json",
                store="notebook",
            ),
        ),
        (
            {
                "name": "foo",
                "data": ["foo", "bar", 1, 2, 3],
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(
                name="foo",
                data=["foo", "bar", 1, 2, 3],
                encoder="json",
                store="notebook",
            ),
        ),
        (
            {
                "name": "foo",
                "data": [u"😍"],
                "encoder": "json",
                "store": "notebook",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(name="foo", data=[u"😍"], encoder="json", store="notebook"),
        ),
        (
            {"name": "foo", "data": [u"😍"], "encoder": "json", "version": 1},
            Scrap(name="foo", data=[u"😍"], encoder="json", store="notebook"),
        ),
    ],
)
def test_payload_to_scrap(test_input, expected):
    assert payload_to_scrap(test_input) == expected


class InvalidData(object):
    pass


@pytest.mark.parametrize(
    "test_input",
    [
        Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder=None, store="notebook"),
        Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="json", store=None),
        Scrap(name="foo", data=None, reference=None, encoder="json", store="notebook"),
        Scrap(
            name="foo",
            data='{"foo":"bar","baz":1}',
            reference="s3://foo/bar.json",
            encoder="json",
            store="notebook",
        ),
        Scrap(
            name=None, data=["foo", "bar", 1, 2, 3], encoder="json", store="notebook"
        ),
        Scrap(name="foo", data=InvalidData(), encoder="custom", store="notebook"),
    ],
)
def test_scrap_to_payload_validation_error(test_input):
    with pytest.raises(ScrapbookDataException):
        print(test_input)
        scrap_to_payload(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        {
            "name": "foo",
            "data": '{"foo":"bar","baz":1}',
            "encoder": None,
            "store": "notebook",
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": "foo",
            "data": '{"foo":"bar","baz":1}',
            "encoder": "notebook",
            "store": None,
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": "foo",
            "data": None,
            "encoder": "json",
            "store": "notebook",
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": None,
            "data": ["foo", "bar", 1, 2, 3],
            "encoder": "json",
            "store": "notebook",
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": "foo",
            "data": InvalidData(),
            "encoder": "custom",
            "store": "notebook",
            "version": LATEST_SCRAP_VERSION,
        },
    ],
)
def test_payload_to_scrap_validation_error(test_input):
    with pytest.raises(ScrapbookDataException):
        payload_to_scrap(test_input)


@mock.patch("scrapbook.scraps.logger")
def test_payload_to_scrap_later_version(mock_logging):
    assert payload_to_scrap(
        {
            "name": "foo",
            "data": {"foo": "bar", "baz": 1},
            "encoder": "json",
            "version": LATEST_SCRAP_VERSION + 1,
        }
    ) == Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json")
    # Should emit a warning that it might not be able to parse the payload
    assert mock_logging.warning.called


@mock.patch("scrapbook.scraps.logger")
def test_payload_to_scrap_later_version_mismatch(mock_logging):
    # Try as best as can be done to match fields when version is higher
    assert payload_to_scrap(
        {
            "changed_": "foo",
            "changed_data": {"foo": "bar", "baz": 1},
            "changed_encoder": "json",
            "version": LATEST_SCRAP_VERSION + 1,
        }
    ) == Scrap(name=None, data=None, encoder=None)
    # Should emit a warning that it might not be able to parse the payload
    assert mock_logging.warning.called
