#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import pytest
import collections

from IPython.display import Image

from . import get_fixture_path
from ..models import GLUE_OUTPUT_PREFIX
from ..api import glue, frame

@pytest.mark.parametrize(
    "name,scrap,storage,data",
    [
        (
            'foobarbaz',
            {"foo":"bar","baz":1},
            None,
            {
                GLUE_OUTPUT_PREFIX + 'json': {
                    'foobarbaz': {"foo":"bar","baz":1}
                }
            }
        ),
        (
            'foobarbaz',
            '{"foo":"bar","baz":1}',
            None,
            {
                GLUE_OUTPUT_PREFIX + 'unicode': {
                    'foobarbaz': '{"foo":"bar","baz":1}'
                }
            }
        ),
        (
            'foobarbaz',
            '{"foo":"bar","baz":1}',
            'json',
            {
                GLUE_OUTPUT_PREFIX + 'json': {
                    'foobarbaz': {"foo":"bar","baz":1}
                }
            }
        ),
        (
            'foobarbaz',
            # Pick something we don't match normally
            collections.OrderedDict({"foo":"bar","baz":1}),
            'json',
            {
                GLUE_OUTPUT_PREFIX + 'json': {
                    'foobarbaz': {"foo":"bar","baz":1}
                }
            }
        ),
    ],
)
@mock.patch('scrapbook.api.ip_display')
def test_glue(mock_display, name, scrap, storage, data):
    glue(name, scrap, storage)
    mock_display.assert_called_once_with(data, raw=True)

@pytest.mark.parametrize(
    "name,obj,data,metadata",
    [
        (
            'foobarbaz',
            'foo,bar,baz',
            {'text/plain': "'foo,bar,baz'"},
            {'scrapbook': {'name': 'foobarbaz'}},
        ),
        (
            'tinypng',
            Image(filename=get_fixture_path('tiny.png')),
            {
                'image/png': 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4gwRBREo2qqE0wAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAFklEQVQI12P8//8/AwMDEwMDAwMDAwAkBgMBvR7jugAAAABJRU5ErkJggg==\n',
                'text/plain': '<IPython.core.display.Image object>'
            },
            {'scrapbook': {'name': 'tinypng'}},
        ),
    ],
)
@mock.patch('scrapbook.api.ip_display')
def test_frame(mock_display, name, obj, data, metadata):
    frame(name, obj)
    mock_display.assert_called_once_with(data, metadata=metadata, raw=True)
