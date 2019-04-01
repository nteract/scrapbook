#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six
import mock
import pytest
import collections

from IPython.display import Image

from . import get_fixture_path
from ..api import glue
from ..schemas import GLUE_PAYLOAD_FMT, LATEST_SCRAP_VERSION


@pytest.mark.parametrize(
    "name,scrap,encoder,data,metadata",
    [
        (
            "foobarbaz",
            {"foo": "bar", "baz": 1},
            "text",
            {
                GLUE_PAYLOAD_FMT.format(encoder="text"): {
                    "name": "foobarbaz",
                    "data": str({"foo": "bar", "baz": 1}),
                    "encoder": "text",
                    "store": "notebook",
                    "stored_format": "unicode",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {"scrapbook": {"name": "foobarbaz", "data": True, "display": False}},
        ),
        (
            "foobarbaz",
            '{"foo":"bar","baz":1}',
            "text",
            {
                GLUE_PAYLOAD_FMT.format(encoder="text"): {
                    "name": "foobarbaz",
                    "data": '{"foo":"bar","baz":1}',
                    "encoder": "text",
                    "store": "notebook",
                    "stored_format": "unicode",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {"scrapbook": {"name": "foobarbaz", "data": True, "display": False}},
        ),
        (
            "foobarbaz",
            '{"foo":"bar","baz":1}',
            "json",
            {
                GLUE_PAYLOAD_FMT.format(encoder="json"): {
                    "name": "foobarbaz",
                    "data": '{"foo":"bar","baz":1}',
                    "encoder": "json",
                    "store": "notebook",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {"scrapbook": {"name": "foobarbaz", "data": True, "display": False}},
        ),
        (
            "foobarbaz",
            # Pick something we don't match normally
            collections.OrderedDict({"foo": "bar", "baz": 1}),
            "json",
            {
                GLUE_PAYLOAD_FMT.format(encoder="json"): {
                    "name": "foobarbaz",
                    "data": {"foo": "bar", "baz": 1},
                    "encoder": "json",
                    "store": "notebook",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {"scrapbook": {"name": "foobarbaz", "data": True, "display": False}},
        ),
    ],
)
@mock.patch("scrapbook.api.ip_display")
def test_glue(mock_display, name, scrap, encoder, data, metadata):
    glue(name, scrap, encoder)
    mock_display.assert_called_once_with(data, metadata=metadata, raw=True)


@pytest.mark.parametrize(
    "name,obj,data,encoder,metadata,display",
    [
        (
            "foobarbaz",
            "foo,bar,baz",
            {u"text/plain": u"'foo,bar,baz'"},
            "display",  # Prevent data saves
            {u"scrapbook": {u"name": u"foobarbaz", "data": False, "display": True}},
            None,  # This should default into True
        ),
        (
            "tinypng",
            Image(filename=get_fixture_path("tiny.png")),
            {
                u"image/png": (
                    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4gwRBREo2qqE0wAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAFklEQVQI12P8//8/AwMDEwMDAwMDAwAkBgMBvR7jugAAAABJRU5ErkJggg==\n"  # noqa: E501
                    if six.PY3
                    else "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x02\x00\x00\x00\x02\x08\x02\x00\x00\x00\xfd\xd4\x9as\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xe2\x0c\x11\x05\x11(\xda\xaa\x84\xd3\x00\x00\x00\x1diTXtComment\x00\x00\x00\x00\x00Created with GIMPd.e\x07\x00\x00\x00\x16IDAT\x08\xd7c\xfc\xff\xff?\x03\x03\x03\x13\x03\x03\x03\x03\x03\x03\x00$\x06\x03\x01\xbd\x1e\xe3\xba\x00\x00\x00\x00IEND\xaeB`\x82"  # noqa: E501
                ),
                u"text/plain": u"<IPython.core.display.Image object>",
            },
            "display",  # Prevent data saves
            {"scrapbook": {"name": "tinypng", "data": False, "display": True}},
            True,
        ),
        (
            "tinypng",
            Image(filename=get_fixture_path("tiny.png")),
            {u"text/plain": u"<IPython.core.display.Image object>"},
            "display",  # Prevent data saves
            {"scrapbook": {"name": "tinypng", "data": False, "display": True}},
            ("text/plain",),  # Pick content of display
        ),
        (
            "tinypng",
            Image(filename=get_fixture_path("tiny.png")),
            {u"text/plain": u"<IPython.core.display.Image object>"},
            "display",  # Prevent data saves
            {"scrapbook": {"name": "tinypng", "data": False, "display": True}},
            {"exclude": "image/png"},  # Exclude content of display
        ),
        (
            "tinypng",
            Image(filename=get_fixture_path("tiny.png")),
            {},  # Should have no matching outputs
            "display",  # Prevent data saves
            {"scrapbook": {"name": "tinypng", "data": False, "display": True}},
            ("n/a",),  # Pick content of display
        ),
    ],
)
@mock.patch("scrapbook.api.ip_display")
def test_glue_display_only(mock_display, name, obj, data, encoder, metadata, display):
    glue(name, obj, encoder=encoder, display=display)
    mock_display.assert_called_once_with(data, metadata=metadata, raw=True)


@pytest.mark.parametrize(
    "name,obj,data_output,display_output,encoder,data_metadata,display_metadata,display",
    [
        (
            "foobarbaz",
            "foo,bar,baz",
            {
                GLUE_PAYLOAD_FMT.format(encoder="text"): {
                    "name": "foobarbaz",
                    "data": "foo,bar,baz",
                    "encoder": "text",
                    "store": "notebook",
                    "stored_format": "unicode",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {u"text/plain": u"'foo,bar,baz'"},
            "text",  # Save data as text
            {u"scrapbook": {u"name": u"foobarbaz", "data": True, "display": False}},
            {u"scrapbook": {u"name": u"foobarbaz", "data": False, "display": True}},
            True,  # Indicate display should also be available
        ),
        (
            "foobarbaz",
            ["foo", "bar", "baz"],
            {
                GLUE_PAYLOAD_FMT.format(encoder="json"): {
                    "name": "foobarbaz",
                    "data": ["foo", "bar", "baz"],
                    "encoder": "json",
                    "store": "notebook",
                    "version": LATEST_SCRAP_VERSION,
                }
            },
            {u"text/plain": u"['foo', 'bar', 'baz']"},
            None,  # Save data as default
            {u"scrapbook": {u"name": u"foobarbaz", "data": True, "display": False}},
            {u"scrapbook": {u"name": u"foobarbaz", "data": False, "display": True}},
            True,  # Indicate display should also be available
        ),
    ],
)
@mock.patch("scrapbook.api.ip_display")
def test_glue_plus_display(
    mock_display,
    name,
    obj,
    data_output,
    display_output,
    encoder,
    data_metadata,
    display_metadata,
    display,
):
    glue(name, obj, encoder=encoder, display=display)
    mock_display.assert_has_calls(
        [
            mock.call(data_output, metadata=data_metadata, raw=True),
            mock.call(display_output, metadata=display_metadata, raw=True),
        ]
    )
