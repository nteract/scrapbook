papermill record
================

**scrapbook** provides a robust and flexible recording schema. This
library is intended to replace
`papermill <https://papermill.readthedocs.io>`__'s existing ``record``
functionality.

`Documentation for papermill
record <https://papermill.readthedocs.io/en/latest/usage-recording.html?#recording-values-to-the-notebook>`__
In brief:

``pm.record(name, value)``: enabled users the ability to record values
to be saved with the notebook `[API
documentation] <https://papermill.readthedocs.io/en/latest/reference/papermill.html#papermill.api.record>`__

.. code:: python

    pm.record("hello", "world")
    pm.record("number", 123)
    pm.record("some_list", [1, 3, 5])
    pm.record("some_dict", {"a": 1, "b": 2})

``pm.read_notebook(notebook)``: pandas could be used later to recover
recorded values by reading the output notebook into a dataframe.

.. code:: python

    nb = pm.read_notebook('notebook.ipynb')
    nb.dataframe

Limitations and challenges
--------------------------

-  The ``record`` function didn't follow papermill's pattern of linear
   execution of a notebook codebase. (It was awkward to describe
   ``record`` as an additional feature of papermill this week. It really
   felt like describing a second less developed library.)
-  Recording / Reading required data translation to JSON for everything.
   This is a tedious, painful process for dataframes.
-  Reading recorded values into a dataframe would result in unintuitive
   dataframe shapes.
-  Less modularity and flexiblity than other papermill components where
   custom operators can be registered.
