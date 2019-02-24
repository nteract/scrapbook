.. _models:

Models
======

A few new names for information are introduced in scrapbook:

-  **scraps**: serializable data values and visualizations such as
   strings, lists of objects, pandas dataframes, charts, images, or data
   references.
-  **notebook**: a wrapped nbformat notebook object with extra methods
   for interacting with scraps.
-  **scrapbook**: a collection of notebooks with an interface for asking
   questions of the collection.
-  **encoders**: a registered translator of data to/from notebook
   storage formats.

.. _scrap_model:

Scrap
-----

The scrap model houses a few key attributes in a tuple. Namely:

-  **name**: The name of the scrap
-  **data**: Any data captured by the scrapbook api call
-  **encoder**: The name of the encoder used to encode/decode data
   to/from the notebook
-  **display**: Any display data used by IPython to display visual
   content

.. _notebook_model:

Notebook
--------

The Notebook object adheres to the `nbformat's json
schema <https://github.com/jupyter/nbformat/blob/master/nbformat/v4/nbformat.v4.schema.json>`__,
allowing for access to its required fields.

.. code:: python

    nb = sb.read_notebook('notebook.ipynb')
    nb.cells # The cells from the notebook
    nb.metadata
    nb.nbformat
    nb.nbformat_minor

There's a few additional methods provided, outlined in the API page (:ref:`read_notebook_usage`)

.. _scrapbook_model:

Scrapbook
---------

A collection of Notebooks is called a Scrapbook. It allows for access the underlying notebooks and to perform data collection from the group as a whole.

.. code:: python

    # create a scrapbook named `book`
    book = sb.read_notebooks('path/to/notebook/collection/')
    # get the underlying notebooks as a list
    book.notebooks # Or `book.values`

There's a additional methods provided, outlined in the API page (:ref:`read_notebooks_usage`)

.. _encoder_model:

Encoder
-------

Encoders are accessible by key names to Encoder objects registered
against the ``encoders.registry`` object. To register new data encoders
simply call:

.. code:: python

    from encoder import registry as encoder_registry
    # add encoder to the registry
    encoder_registry.register("custom_encoder_name", MyCustomEncoder())

The encode class must implement two methods, ``encode`` and ``decode``:

.. code:: python

    class MyCustomEncoder(object):
        def encode(self, scrap):
            # scrap.data is any type, usually specific to the encoder name
            pass  # Return a `Scrap` with `data` type one of [None, list, dict, *six.integer_types, *six.string_types]

        def decode(self, scrap):
            # scrap.data is one of [None, list, dict, *six.integer_types, *six.string_types]
            pass  # Return a `Scrap` with `data` type as any type, usually specific to the encoder name

This can read transform scraps into a json object representing their
contents or location and load those strings back into the original data
objects.

``text``
~~~~~~~~

A basic string storage format that saves data as python strings.

.. code:: python

    sb.glue("hello", "world", "text")

``json``
~~~~~~~~

.. code:: python

    sb.glue("foo_json", {"foo": "bar", "baz": 1}, "json")

``arrow``
~~~~~~~~~

Implementation Pending!
