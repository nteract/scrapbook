.. _read_notebooks_usage:

read_notebooks API
==================

Reads all notebooks located in a given ``path`` into a :ref:`scrapbook_model` object.

.. code:: python

    # create a scrapbook named `book`
    book = sb.read_notebooks('path/to/notebook/collection/')
    # get the underlying notebooks as a list
    book.notebooks # Or `book.values`

The path reuses `papermill's registered
iorw <https://papermill.readthedocs.io/en/latest/reference/papermill-io.html>`_.
to list and read files form various sources, such that non-local urls
can load data.

.. code:: python

    # create a scrapbook named `book`
    book = sb.read_notebooks('s3://bucket/key/prefix/to/notebook/collection/')

The Scrapbook (``book`` in this example) can be used to recall all
scraps across the collection of notebooks:

.. code:: python

    book.notebook_scraps # Dict of shape `notebook` -> (`name` -> `scrap`)
    book.scraps # merged dict of shape `name` -> `scrap`

.. _scrapbook_scraps_report:

scraps_report
-------------

The Scrapbook collection can be used to generate a ``scraps_report`` on
all the scraps from the collection as a markdown structured output.

.. code:: python

    book.scraps_report()

This display can filter on scrap and notebook names, as well as enable
or disable an overall header for the display.

.. code:: python

    book.scraps_report(
      scrap_names=["scrap1", "scrap2"],
      notebook_names=["result1"], # matches `/notebook/collections/result1.ipynb` pathed notebooks
      header=False
    )

By default the report will only populate with visual elements. To also
report on data elements set include_data.

.. code:: python

    book.scraps_report(include_data=True)

papermill support
-----------------

Finally the scrapbook has two backwards compatible features for
deprecated ``papermill`` capabilities:

.. code:: python

    book.papermill_dataframe
    book.papermill_metrics
