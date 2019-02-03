<!---(binder links generated at https://mybinder.readthedocs.io/en/latest/howto/badges.html and compressed at https://tinyurl.com) -->
[![Build Status](https://travis-ci.org/nteract/scrapbook.svg?branch=master)](https://travis-ci.org/nteract/scrapbook)
[![image](https://codecov.io/github/nteract/scrapbook/coverage.svg?branch=master)](https://codecov.io/github/nteract/scrapbook=master)
[![Documentation Status](https://readthedocs.org/projects/nteract-scrapbook/badge/?version=latest)](https://nteract-scrapbook.readthedocs.io/en/latest/?badge=latest)
[![badge](https://tinyurl.com/ybk8qa3j)](https://mybinder.org/v2/gh/nteract/scrapbook/master?filepath=binder%2FResultsDemo.ipynb)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# scrapbook

A library for recording a notebook’s data values (scraps) and generated content (highlights). These recorded scraps and snaps can be read at a future time.

Two new names for information are introduced in scrapbook:

- **scraps**: serializable data values such as strings, lists of objects, pandas dataframes, or data table references.
- **highlights**: named displays of information such as a generated image, plot, or UI message which encapsulate information but do not store the underlying data.

## Use Case

Notebook users may wish to record data produced during a notebook execution.
This recorded data can then be read to be used at a later time or be passed to
another notebook as input.

Namely scrapbook lets you:
- **persist** data (scraps) in a notebook
- **highlight** named displays (highlights) in notebooks
- **recall** any persisted scrap of data or highlight
- **summarize collections** of notebooks

## API Calls

Scrapbook adds a few basic api commands which enable saving and retrieving data.

### glue

Records a scrap (data value) in the given notebook cell.

The scrap (recorded value) can be retrieved during later inspection of the output notebook.

```python
sb.glue("hello", "world")
sb.glue("number", 123)
sb.glue("some_list", [1, 3, 5])
sb.glue("some_dict", {"a": 1, "b": 2})
sb.glue("non_json", df, 'arrow')
```

The scrapbook library can be used later to recover scraps (recorded values)  from the output notebook

```python
nb = sb.read_notebook('notebook.ipynb')
nb.scraps
```

The storage format of the scraps is implied by the value type any registered data translators, but can be overwritten by setting the `storage` argument to a particular translator's registered name (e.g. `"json"`).

This data is persisted by generating a display output with a special media type identifying the content storage format and data. These outputs are not visible in notebook rendering but still exist in the document. Scrapbook then can rehydrate the data associated with the notebook in the future by reading these cell outputs. 

### highlight

Display a highlight (an object with the reference `name` in a retrievable manner). Unlike `glue` this is intended to generate a highlight (visible display output) for notebook interfaces to render.

```python
sb.highlight("hello", "Hello World")
sb.highlight("sharable_png", IPython.display.Image(filename=get_fixture_path("sharable.png")))
```

Like scraps these can be retrieved at a later time, though they don't cary any actual data, just the display result of some object.

```python
nb = sb.read_notebook('notebook.ipynb')
nb.highlights
```

More usefully, you can copy highlights from earlier executions to re-display the object in the current notebook.

```python
nb = sb.read_notebook('notebook.ipynb')
nb.copy_highlight("sharable_png")
```

### read_notebook

Reads a Notebook object loaded from the location specified at `path`. You've already seen how this function is used in the above api calls, but essentially this provides a thin wrapper over an nbformat notebook object with the ability to extract scrapbook scraps and highlights.

```python
nb = sb.read_notebook('notebook.ipynb')
```

The Notebook object also has a few legacy functions for backwards compatability with papermill's Notebook object model. As a result it can be used to read papermill execution statistics as well as scrapbook abstractions.

```python
nb.cell_timing
nb.execution_counts
nb.papermill_metrics
nb.parameter_dataframe
nb.papermill_dataframe
```

The notebook reader relies on [papermill's registered iorw](https://papermill.readthedocs.io/en/latest/reference/papermill-io.html) to enable access to a variety of sources such as -- but not limited to -- S3, Azure, and Google Cloud.

### read_notebooks

Reads all notebooks in a given `path` into a Scrapbook object.

```python
book = sb.read_notebooks('path/to/notebook/collection/')
book.sorted_notebooks # get the underlying notebooks as a list
```

The Scrapbook can be used to recall all scraps across the collection:
```python
book.scraps # Map of {notebook -> {name -> scrap}}
book.flat_scraps # Map of {name -> scrap}
```

Or to collect highlights:

```python
book.highlights # Map of {notebook -> {name -> highlight}}
book.flat_highlights # Map of {name -> highlight}
```

The Scrapbook collection can be used to display all the highlights from the collection as a markdown structured output as well.

```python
book.display()
```

This display can filter on highlight names and keys, as well as enable or disable an overall header for the display.

Finally the scrapbook has two backwards compatible features for deprecated papermill capabilities:

```python
book.papermill_dataframe
book.papermill_metrics
```

This function also relies on [papermill's registered iorw](https://papermill.readthedocs.io/en/latest/reference/papermill-io.html) to list and read files form various sources.

## Storage Formats

Storage formats are accessible by key names to Translator objects registered against the `translators.registry` object. To register new data translator / loaders simple call

```python
registry.register("custom_store_name", MyCustomTranslator())
```

The store class must implement two methods:
```python
class MyCustomTranslator(object):
    def translate(self, scrap):
        pass  # TODO: Implement

    def load(self, scrap):
        pass  # TODO: Implement
```

which can read transform scraps into a string representing their contents or location and load those strings back into the original data objects.

### unicode

A basic string storage format that saves data as python strings.

```python
sb.glue("hello", "world", "unicode")
```

### json

```python
sb.glue("foo_json", {"foo": "bar", "baz": 1}, "json")
```

### arrow

Implementation Pending!

## papermill's deprecated record feature

**scrapbook** provides a robust and flexible recording schema. This library is
intended to replace [papermill](https://papermill.readthedocs.io)'s existing
`record` functionality.

[Documentation for papermill record](https://papermill.readthedocs.io/en/latest/usage.html#recording-values-to-the-notebook)
In brief:

`pm.record(name, value)`: enabled users the ability to record values to be saved
with the notebook [[API documentation]](https://papermill.readthedocs.io/en/latest/reference/papermill.html#papermill.api.record)

```python
pm.record("hello", "world")
pm.record("number", 123)
pm.record("some_list", [1, 3, 5])
pm.record("some_dict", {"a": 1, "b": 2})
```

`pm.read_notebook(notebook)`: pandas could be used later to recover recorded values by reading the output notebook into a dataframe.

```python
nb = pm.read_notebook('notebook.ipynb')
nb.dataframe
```

### Limitations and challenges

- The `record` function didn't follow papermill's pattern of linear execution
  of a notebook codebase. (It was awkward to describe `record` as an additional
  feature of papermill this week. It really felt like describing a second less 
  developed library.)
- Recording / Reading required data translation to JSON for everything. This is
  a tedious, painful process for dataframes.
- Reading recorded values into a dataframe would result in unintuitive dataframe
  shapes.
- Less modularity and flexiblity than other papermill components where custom
  operators can be registered.


