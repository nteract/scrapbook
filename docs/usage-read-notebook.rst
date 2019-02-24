.. _read_notebook_usage:

read_notebook API
=================

Reads a :ref:`notebook_model` object loaded from the location specified at ``path``.
You've already seen how this function is used in the above api call
examples, but essentially this provides a thin wrapper over an
``nbformat``'s NotebookNode with the ability to extract scrapbook
scraps.

.. code:: python

    nb = sb.read_notebook('notebook.ipynb')

This Notebook object adheres to the `nbformat's json
schema <https://github.com/jupyter/nbformat/blob/master/nbformat/v4/nbformat.v4.schema.json>`__,
allowing for access to its required fields.

.. code:: python

    nb.cells # The cells from the notebook
    nb.metadata
    nb.nbformat
    nb.nbformat_minor

There's a few additional methods provided, most of which are outlined in
more detail below:

.. code:: python

    nb.scraps
    nb.reglue

The abstraction also makes saved content available as a dataframe
referencing each key and source. More of these methods will be made
available in later versions.

.. code:: python

    # Produces a data frame with ["name", "data", "encoder", "display", "filename"] as columns
    nb.scrap_dataframe # Warning: This might be a large object if data or display is large

The Notebook object also has a few legacy functions for backwards
compatibility with papermill's Notebook object model. As a result, it
can be used to read papermill execution statistics as well as scrapbook
abstractions:

.. code:: python

    nb.cell_timing # List of cell execution timings in cell order
    nb.execution_counts # List of cell execution counts in cell order
    nb.papermill_metrics # Dataframe of cell execution counts and times
    nb.papermill_record_dataframe # Dataframe of notebook records (scraps with only data)
    nb.parameter_dataframe # Dataframe of notebook parameters
    nb.papermill_dataframe # Dataframe of notebook parameters and cell scraps

The notebook reader relies on `papermill's registered
iorw <https://papermill.readthedocs.io/en/latest/reference/papermill-io.html>`__
to enable access to a variety of sources such as -- but not limited to
-- S3, Azure, and Google Cloud.

.. _notebook_scraps:

scraps
------

The ``scraps`` method allows for access to all of the scraps in a
particular notebook by providing a name -> scrap lookup.

.. code:: python

    nb = sb.read_notebook('notebook.ipynb')
    nb.scraps # Prints a dict of all scraps by name

This object has a few additional methods as well for convenient
conversion and execution.

.. code:: python

    nb.scraps.data_scraps # Filters to only scraps with `data` associated
    nb.scraps.data_dict # Maps `data_scraps` to a `name` -> `data` dict
    nb.scraps.display_scraps # Filters to only scraps with `display` associated
    nb.scraps.display_dict # Maps `display_scraps` to a `name` -> `display` dict
    nb.scraps.dataframe # Generates a dataframe with ["name", "data", "encoder", "display"] as columns

These methods allow for simple use-cases to not require digging through
model abstractions.

.. _notebook_reglue:

reglue
------

Using ``reglue`` one can take any scrap glue'd into one notebook and
glue into the current one.

.. code:: python

    nb = sb.read_notebook('notebook.ipynb')
    nb.reglue("table_scrap") # This copies both data and displays

Any data or display information will be copied verbatim into the
currently executing notebook as though the user called ``glue`` again on
the original source.

It's also possible to rename the scrap in the process.

.. code:: python

    nb.reglue("table_scrap", "old_table_scrap")

And finally if one wishes to try to reglue without checking for
existence the ``raise_on_missing`` can be set to just display a message
on failure.

.. code:: python

    nb.reglue("maybe_missing", raise_on_missing=False)
    # => "No scrap found with name 'maybe_missing' in this notebook"
