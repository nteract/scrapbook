# -*- coding: utf-8 -*-
"""
api.py

Provides the base API calls for scrapbook
"""
from __future__ import unicode_literals
import os

import IPython

from six import string_types
from IPython.display import display as ip_display
# We lean on papermill's readers to connect to remote stores
from papermill.iorw import list_notebook_files

from .models import Notebook, Scrapbook, GLUE_OUTPUT_PREFIX
from .translators import registry as translator_registry


def glue(name, scrap, storage=None):
    """
    Record a value in the output notebook when a cell is executed.

    The recorded value can be retrieved during later inspection of the
    output notebook.

    Example
    -------
    `record` provides a handy way for data to be stored with a notebook to
    be used later::

        sb.glue("hello", "world")
        sb.glue("number", 123)
        sb.glue("some_list", [1, 3, 5])
        sb.glue("some_dict", {"a": 1, "b": 2})
        sb.glue("non_json", df, 'arrow')

    scrapbook can be used later to recover recorded values by
    reading the output notebook

        nb = sb.read_notebook('notebook.ipynb')
        nb.scraps

    Parameters
    ----------
    name: str
        Name of the value to record.
    scrap: any
        The value to record.
    storage: str (optional)
        The data protocol name to respect in persisting data
    """

    # TODO: Implement the cool stuff. Remote storage indicators?!? Maybe remote media type?!?
    # TODO: Make this more modular
    # TODO: Use translators to determine best storage type
    # ...
    if not storage:
        if isinstance(scrap, string_types):
            storage = 'unicode'
        elif isinstance(scrap, (list, dict)):
            storage = 'json'
        else:
            # This may be more complex in the future
            storage = 'json'
    data = {
        GLUE_OUTPUT_PREFIX + storage: {
            name: translator_registry.translate_data(storage, scrap)
        }
    }

    # IPython.display.display takes a tuple of objects as first parameter
    # `http://ipython.readthedocs.io/en/stable/api/generated/IPython.display.html#IPython.display.display`
    ip_display(data, raw=True)


def highlight(name, obj):
    """
    Display an object with the reference `name` in a retrievable manner.

    Parameters
    ----------
    name : str
        Name of the output.
    obj : object
        An object that can be displayed in the notebook.

    """
    data, metadata = IPython.core.formatters.format_display_data(obj)
    metadata['scrapbook'] = dict(name=name)
    ip_display(data, metadata=metadata, raw=True)


def read_notebook(path):
    """
    Returns a Notebook object loaded from the location specified at `path`.

    Parameters
    ----------
    path : str
        Path to a notebook `.ipynb` file.

    Returns
    -------
    notebook : object
        A Notebook object.

    """
    return Notebook(path)


def read_notebooks(path):
    """
    Returns a Scrapbook including the notebooks read from the
    directory specified by `path`.

    Parameters
    ----------
    path : str
        Path to directory containing notebook `.ipynb` files.

    Returns
    -------
    scrapbook : object
        A `Scrapbook` object.

    """
    scrapbook = Scrapbook()
    for notebook_path in list_notebook_files(path):
        fn = os.path.splitext(os.path.basename(notebook_path))[0]
        scrapbook[fn] = read_notebook(notebook_path)
    return scrapbook
