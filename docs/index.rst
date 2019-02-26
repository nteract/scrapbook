Welcome to scrapbook
====================

.. image:: https://travis-ci.org/nteract/scrapbook.svg?branch=master
   :target: https://travis-ci.org/nteract/scrapbook
.. image:: https://codecov.io/github/nteract/scrapbook/coverage.svg?branch=master
   :target: https://codecov.io/github/nteract/scrapbook?branch=master
.. image:: https://readthedocs.org/projects/scrapbook/badge/?version=latest
   :target: http://nteract-scrapbook.readthedocs.io/en/latest/?badge=latest
.. image:: https://tinyurl.com/y3moqkmc
   :target: https://mybinder.org/v2/gh/nteract/scrapbook/master?filepath=binder%2Freglue_highlight_dates.ipynb
.. image:: https://tinyurl.com/ybk8qa3j
   :target: https://mybinder.org/v2/gh/nteract/scrapbook/master?filepath=binder%2FResultsDemo.ipynb
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black

**scrapbook** is a library for recording a notebook’s data values and
generated visual content as "scraps". These recorded scraps can be read
at a future time.

This library replaces `papermill <https://papermill.readthedocs.io>`_'s existing
`record` functionality.

Python Version Support
----------------------

This library will support python 2.7 and 3.5+ until end-of-life for
python 2 in 2020. After which python 2 support will halt and only 3.x
version will be maintained.

Use Case
--------

Notebook users may wish to record data produced during a notebook
execution. This recorded data can then be read to be used at a later
time or be passed to another notebook as input.

Namely scrapbook lets you:

-  **persist** data and displays (scraps) in a notebook
-  **recall** any persisted scrap of data
-  **summarize collections** of notebooks

Documentation
-------------

These pages guide you through the installation and usage of scrapbook.

.. toctree::
   :maxdepth: 1

   installation
   models
   usage-glue
   usage-read-notebook
   usage-read-notebooks
   deprecation-papermill

API Reference
-------------

If you are looking for information about a specific function, class, or method,
this documentation section will help you.

.. toctree::
   :maxdepth: 3

   reference/modules.rst
   reference/scrapbook.tests.rst

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
