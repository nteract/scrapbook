#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import pytest

from ..scraps import Scrap, scrap_to_payload, payload_to_scrap
from ..schemas import LATEST_SCRAP_VERSION
from ..exceptions import ScrapbookDataException


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
            {
                "name": "foo",
                "data": '{"foo":"bar","baz":1}',
                "encoder": "text",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
            {
                "name": "foo",
                "data": {"foo": "bar", "baz": 1},
                "encoder": "json",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
            {
                "name": "foo",
                "data": ["foo", "bar", 1, 2, 3],
                "encoder": "json",
                "version": LATEST_SCRAP_VERSION,
            },
        ),
        (
            Scrap(name="foo", data=[u"😍"], encoder="json"),
            {
                "name": "foo",
                "data": [u"😍"],
                "encoder": "json",
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
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder="text"),
        ),
        (
            {
                "name": "foo",
                "data": {"foo": "bar", "baz": 1},
                "encoder": "json",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(name="foo", data={"foo": "bar", "baz": 1}, encoder="json"),
        ),
        (
            {
                "name": "foo",
                "data": ["foo", "bar", 1, 2, 3],
                "encoder": "json",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(name="foo", data=["foo", "bar", 1, 2, 3], encoder="json"),
        ),
        (
            {
                "name": "foo",
                "data": [u"😍"],
                "encoder": "json",
                "version": LATEST_SCRAP_VERSION,
            },
            Scrap(name="foo", data=[u"😍"], encoder="json"),
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
        Scrap(name="foo", data='{"foo":"bar","baz":1}', encoder=None),
        Scrap(name="foo", data=None, encoder="json"),
        Scrap(name=None, data=["foo", "bar", 1, 2, 3], encoder="json"),
        Scrap(name="foo", data=InvalidData(), encoder="custom"),
    ],
)
def test_scrap_to_payload_validation_error(test_input):
    with pytest.raises(ScrapbookDataException):
        scrap_to_payload(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        {
            "name": "foo",
            "data": '{"foo":"bar","baz":1}',
            "encoder": None,
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": "foo",
            "data": None,
            "encoder": "json",
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": None,
            "data": ["foo", "bar", 1, 2, 3],
            "encoder": "json",
            "version": LATEST_SCRAP_VERSION,
        },
        {
            "name": "foo",
            "data": InvalidData(),
            "encoder": "custom",
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
