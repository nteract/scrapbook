#!/usr/bin/env python
# -*- coding: utf-8 -*-
import six
import mock
import pytest
import collections

from IPython.display import Image

from . import get_fixture_path
from ..models import GLUE_OUTPUT_PREFIX
from ..api import glue, sketch


@pytest.mark.parametrize(
    "name,scrap,storage,data",
    [
        (
            "foobarbaz",
            {"foo": "bar", "baz": 1},
            None,
            {GLUE_OUTPUT_PREFIX + "json": {"foobarbaz": {"foo": "bar", "baz": 1}}},
        ),
        (
            "foobarbaz",
            '{"foo":"bar","baz":1}',
            None,
            {GLUE_OUTPUT_PREFIX + "unicode": {"foobarbaz": '{"foo":"bar","baz":1}'}},
        ),
        (
            "foobarbaz",
            '{"foo":"bar","baz":1}',
            "json",
            {GLUE_OUTPUT_PREFIX + "json": {"foobarbaz": {"foo": "bar", "baz": 1}}},
        ),
        (
            "foobarbaz",
            # Pick something we don't match normally
            collections.OrderedDict({"foo": "bar", "baz": 1}),
            "json",
            {GLUE_OUTPUT_PREFIX + "json": {"foobarbaz": {"foo": "bar", "baz": 1}}},
        ),
    ],
)
@mock.patch("scrapbook.api.ip_display")
def test_glue(mock_display, name, scrap, storage, data):
    glue(name, scrap, storage)
    mock_display.assert_called_once_with(data, raw=True)


@pytest.mark.parametrize(
    "name,obj,data,metadata",
    [
        (
            "foobarbaz",
            "foo,bar,baz",
            {u"text/plain": u"'foo,bar,baz'"},
            {u"scrapbook": {u"name": u"foobarbaz"}},
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
            {"scrapbook": {"name": "tinypng"}},
        ),
    ],
)
@mock.patch("scrapbook.api.ip_display")
def test_sketch(mock_display, name, obj, data, metadata):
    sketch(name, obj)
    mock_display.assert_called_once_with(data, metadata=metadata, raw=True)
