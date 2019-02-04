#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mock
import pytest

import pandas as pd

from IPython.display import Markdown
from pandas.util.testing import assert_frame_equal

from . import get_notebook_path
from .. import read_notebooks
from ..exceptions import ScrapbookException


@pytest.fixture
def notebook_collection():
    path = get_notebook_path("collection")
    return read_notebooks(path)


def test_assign_from_path(notebook_collection):
    notebook_collection["result_no_exec.ipynb"] = get_notebook_path(
        "result_no_exec.ipynb"
    )


def test_scraps(notebook_collection):
    assert notebook_collection.scraps == {
        "result1": {
            "dict": {u"a": 1, u"b": 2},
            "list": [1, 2, 3],
            "number": 1,
            "one": 1,
        },
        "result2": {
            "dict": {u"a": 3, u"b": 4},
            "list": [4, 5, 6],
            "number": 2,
            "two": 2,
        },
    }


def test_flat_scraps(notebook_collection):
    assert notebook_collection.flat_scraps == {
        "dict": {u"a": 3, u"b": 4},
        "list": [4, 5, 6],
        "number": 2,
        "one": 1,
        "two": 2,
    }


def test_snaps(notebook_collection):
    assert notebook_collection.snaps == {
        "result1": {
            "output": {
                "data": {"text/plain": "'Hello World!'"},
                "metadata": {"papermill": {"name": "output"}},
                "output_type": "display_data",
            },
            "one_only": {
                "data": {"text/plain": "'Just here!'"},
                "metadata": {"scrapbook": {"name": "one_only"}},
                "output_type": "display_data",
            },
        },
        "result2": {
            "output": {
                "data": {"text/plain": "'Hello World 2!'"},
                "metadata": {"papermill": {"name": "output"}},
                "output_type": "display_data",
            },
            "two_only": {
                "data": {"text/plain": "'Just here!'"},
                "metadata": {"scrapbook": {"name": "two_only"}},
                "output_type": "display_data",
            },
        },
    }


def test_flat_snaps(notebook_collection):
    assert notebook_collection.flat_snaps == {
        "output": {
            "data": {"text/plain": "'Hello World 2!'"},
            "metadata": {"papermill": {"name": "output"}},
            "output_type": "display_data",
        },
        "one_only": {
            "data": {"text/plain": "'Just here!'"},
            "metadata": {"scrapbook": {"name": "one_only"}},
            "output_type": "display_data",
        },
        "two_only": {
            "data": {"text/plain": "'Just here!'"},
            "metadata": {"scrapbook": {"name": "two_only"}},
            "output_type": "display_data",
        },
    }


def test_papermill_metrics(notebook_collection):
    expected_df = pd.DataFrame(
        [
            ("result1.ipynb", "Out [1]", 0.0, "time (s)", "result1"),
            ("result1.ipynb", "Out [2]", 0.123, "time (s)", "result1"),
            ("result2.ipynb", "Out [1]", 0.0, "time (s)", "result2"),
            ("result2.ipynb", "Out [2]", 0.456, "time (s)", "result2"),
        ],
        columns=["filename", "cell", "value", "type", "key"],
    )
    assert_frame_equal(notebook_collection.papermill_metrics, expected_df)


def test_papermill_dataframe(notebook_collection):
    expected_df = pd.DataFrame(
        [
            ("bar", "hello", "parameter", "result1.ipynb", "result1"),
            ("foo", 1, "parameter", "result1.ipynb", "result1"),
            ("dict", {u"a": 1, u"b": 2}, "record", "result1.ipynb", "result1"),
            ("list", [1, 2, 3], "record", "result1.ipynb", "result1"),
            ("number", 1, "record", "result1.ipynb", "result1"),
            ("one", 1, "record", "result1.ipynb", "result1"),
            ("bar", "world", "parameter", "result2.ipynb", "result2"),
            ("foo", 2, "parameter", "result2.ipynb", "result2"),
            ("dict", {u"a": 3, u"b": 4}, "record", "result2.ipynb", "result2"),
            ("list", [4, 5, 6], "record", "result2.ipynb", "result2"),
            ("number", 2, "record", "result2.ipynb", "result2"),
            ("two", 2, "record", "result2.ipynb", "result2"),
        ],
        columns=["name", "value", "type", "filename", "key"],
    )
    assert_frame_equal(notebook_collection.papermill_dataframe, expected_df)


class AnyMarkdownWith(Markdown):
    def __eq__(self, other):
        try:
            return self.data == other.data
        except AttributeError:
            return False


@mock.patch("scrapbook.models.ip_display")
def test_display(mock_display, notebook_collection):
    notebook_collection.display()
    mock_display.assert_has_calls(
        [
            mock.call(AnyMarkdownWith("### result1")),
            mock.call(AnyMarkdownWith("#### output")),
            mock.call(
                {u"text/plain": u"'Hello World!'"},
                # We don't re-translate the metadata from older messages
                metadata={u"papermill": {u"name": u"output"}},
                raw=True,
            ),
            mock.call(AnyMarkdownWith("#### one_only")),
            mock.call(
                {u"text/plain": u"'Just here!'"},
                metadata={u"scrapbook": {u"name": u"one_only"}},
                raw=True,
            ),
            mock.call(AnyMarkdownWith("<hr>")),
            mock.call(AnyMarkdownWith("### result2")),
            mock.call(AnyMarkdownWith("#### output")),
            mock.call(
                {u"text/plain": u"'Hello World 2!'"},
                # We don't re-translate the metadata from older messages
                metadata={u"papermill": {u"name": u"output"}},
                raw=True,
            ),
            mock.call(AnyMarkdownWith("#### two_only")),
            mock.call(
                {u"text/plain": u"'Just here!'"},
                metadata={u"scrapbook": {u"name": u"two_only"}},
                raw=True,
            ),
        ]
    )


@mock.patch("scrapbook.models.ip_display")
def test_display_no_header(mock_display, notebook_collection):
    notebook_collection.display(header=None)
    mock_display.assert_has_calls(
        [
            mock.call(
                {u"text/plain": u"'Hello World!'"},
                # We don't re-translate the metadata from older messages
                metadata={u"papermill": {u"name": u"output"}},
                raw=True,
            ),
            mock.call(
                {u"text/plain": u"'Just here!'"},
                metadata={"scrapbook": {"name": "one_only"}},
                raw=True,
            ),
            mock.call(
                {u"text/plain": u"'Hello World 2!'"},
                # We don't re-translate the metadata from older messages
                metadata={u"papermill": {u"name": u"output"}},
                raw=True,
            ),
            mock.call(
                {u"text/plain": u"'Just here!'"},
                metadata={u"scrapbook": {u"name": u"two_only"}},
                raw=True,
            ),
        ]
    )


@pytest.mark.parametrize("keys", [("result2",), (["result2"],)])
@mock.patch("scrapbook.models.ip_display")
def test_display_specific_notebook(mock_display, keys, notebook_collection):
    for key in keys:
        notebook_collection.display(keys=key)
        mock_display.assert_has_calls(
            [
                mock.call(AnyMarkdownWith("### result2")),
                mock.call(AnyMarkdownWith("#### output")),
                mock.call(
                    {"text/plain": "'Hello World 2!'"},
                    # We don't re-translate the metadata from older messages
                    metadata={"papermill": {"name": "output"}},
                    raw=True,
                ),
                mock.call(AnyMarkdownWith("#### two_only")),
                mock.call(
                    {"text/plain": "'Just here!'"},
                    metadata={"scrapbook": {"name": "two_only"}},
                    raw=True,
                ),
            ]
        )


@pytest.mark.parametrize("snaps", [("one_only",), (["one_only"],)])
@mock.patch("scrapbook.models.ip_display")
def test_display_specific_snap(mock_display, snaps, notebook_collection):
    for snap in snaps:
        notebook_collection.display(snaps=snap, header=False)
        mock_display.assert_has_calls(
            [
                mock.call(
                    {"text/plain": "'Just here!'"},
                    metadata={"scrapbook": {"name": "one_only"}},
                    raw=True,
                )
            ]
        )


@mock.patch("scrapbook.models.ip_display")
def test_display_snap_key_mismatches(mock_display, notebook_collection):
    notebook_collection.display(snaps="one_only")
    mock_display.assert_has_calls(
        [
            mock.call(AnyMarkdownWith("### result1")),
            mock.call(AnyMarkdownWith("#### one_only")),
            mock.call(
                {"text/plain": "'Just here!'"},
                metadata={"scrapbook": {"name": "one_only"}},
                raw=True,
            ),
            mock.call(AnyMarkdownWith("<hr>")),
            mock.call(AnyMarkdownWith("### result2")),
            mock.call(AnyMarkdownWith("#### one_only")),
            mock.call("No snap available for one_only"),
        ]
    )


def test_display_missing_snap_error(notebook_collection):
    with pytest.raises(ScrapbookException):
        notebook_collection.display(snaps="one_only", raise_error=True)
