<img width="616" alt="scrapbook logo" src="https://user-images.githubusercontent.com/836375/52512549-31260f00-2bba-11e9-9556-515ba5ff0b4b.png">

# scrapbook

<!---(binder links generated at https://mybinder.readthedocs.io/en/latest/howto/badges.html and compressed at https://tinyurl.com) -->
[![CI](https://github.com/nteract/scrapbook/actions/workflows/ci.yml/badge.svg)](https://github.com/nteract/scrapbook/actions/workflows/ci.yml)
[![image](https://codecov.io/github/nteract/scrapbook/coverage.svg?branch=main)](https://codecov.io/github/nteract/scrapbook=main)
[![Documentation Status](https://readthedocs.org/projects/nteract-scrapbook/badge/?version=latest)](https://nteract-scrapbook.readthedocs.io/en/latest/?badge=latest)
[![badge](https://tinyurl.com/y3moqkmc)](https://mybinder.org/v2/gh/nteract/scrapbook/main?filepath=binder%2Freglue_highlight_dates.ipynb)
[![badge](https://tinyurl.com/ybk8qa3j)](https://mybinder.org/v2/gh/nteract/scrapbook/main?filepath=binder%2FResultsDemo.ipynb)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

The **scrapbook** library records a notebook’s data values and generated visual
content as "scraps". Recorded scraps can be read at a future time.

[See the scrapbook documentation](https://nteract-scrapbook.readthedocs.io/) for
more information on how to use scrapbook.

## Use Cases

Notebook users may wish to record data produced during a notebook's execution.
This recorded data, **scraps**, can be used at a later time or passed in a
workflow to another notebook as input.

Namely, scrapbook lets you:

- **persist** data and visual content displays in a notebook as scraps
- **recall** any persisted scrap of data
- **summarize collections** of notebooks

## Python Version Support

This library's long term support target is Python 3.6+. It currently also
supports Python 2.7 until Python 2 reaches end-of-life in 2020. After this
date, Python 2 support will halt, and only 3.x versions will be maintained.

## Installation

Install using `pip`:

```{.sourceCode .bash}
pip install scrapbook
```

For installing optional IO dependencies, you can specify individual store bundles,
like `s3` or `azure`:

```{.sourceCode .bash}
pip install scrapbook[s3]
```

or use `all`:

```{.sourceCode .bash}
pip install scrapbook[all]
```

---

## Models and Terminology

Scrapbook defines the following items:

- **scraps**: serializable data values and visualizations such as strings, lists of
  objects, pandas dataframes, charts, images, or data references.
- **notebook**: a wrapped nbformat notebook object with extra methods for interacting
  with scraps.
- **scrapbook**: a collection of notebooks with an interface for asking questions of
  the collection.
- **encoders**: a registered translator of data to/from notebook
  storage formats.

### `scrap` model

The `scrap` model houses a few key attributes in a tuple, including:

- **name**: The name of the scrap
- **data**: Any data captured by the scrapbook api call
- **encoder**: The name of the encoder used to encode/decode data to/from the notebook
- **display**: Any display data used by IPython to display visual content

---

## API

Scrapbook adds a few basic api commands which enable saving and retrieving data
including:

- `glue` to persist scraps with or without _display output_
- `read_notebook` reads one notebook
- `scraps` provides a searchable dictionary of all scraps by name
- `reglue` which copies a scrap from another notebook to the current notebook
- `read_notebooks` reads many notebooks from a given path
- `scraps_report` displays a report about collected scraps
- `papermill_dataframe` and `papermill_metrics` for backward compatibility
  for two deprecated papermill features

The following sections provide more detail on these api commands.

### `glue` to persist scraps

Records a `scrap` (data or display value) in the given notebook cell.

The `scrap` (recorded value) can be retrieved during later inspection of the
output notebook.

```python
"""glue example for recording data values"""
import scrapbook as sb

sb.glue("hello", "world")
sb.glue("number", 123)
sb.glue("some_list", [1, 3, 5])
sb.glue("some_dict", {"a": 1, "b": 2})
sb.glue("non_json", df, 'arrow')
```

The scrapbook library can be used later to recover `scraps` from the output
notebook:

```python
# read a notebook and get previously recorded scraps
nb = sb.read_notebook('notebook.ipynb')
nb.scraps
```

**scrapbook** will imply the storage format by the value type of any registered
data encoders. Alternatively, the implied encoding format can be overwritten by
setting the `encoder` argument to the registered name (e.g. `"json"`) of a
particular encoder.

This data is persisted by generating a display output with a special media type
identifying the content encoding format and data. These outputs are not always
visible in notebook rendering but still exist in the document. Scrapbook can
then rehydrate the data associated with the notebook in the future by reading
these cell outputs.

#### With _display output_

To display a named scrap with visible display outputs, you need to indicate that
the scrap is directly renderable.

This can be done by toggling the `display` argument.

```python
# record a UI message along with the input string
sb.glue("hello", "Hello World", display=True)
```

The call will save the data and the display attributes of the Scrap object,
making it visible as well as encoding the original data. This leans on the
`IPython.core.formatters.format_display_data` function to translate the data
object into a display and metadata dict for the notebook kernel to parse.

Another pattern that can be used is to specify that **only the display data**
should be saved, and not the original object. This is achieved by setting
the encoder to be `display`.

```python
# record an image without the original input object
sb.glue("sharable_png",
  IPython.display.Image(filename="sharable.png"),
  encoder='display'
)
```

Finally the media types that are generated can be controlled by passing
a list, tuple, or dict object as the display argument.

```python
sb.glue("media_as_text_only",
  media_obj,
  encoder='display',
  display=('text/plain',) # This passes [text/plain] to format_display_data's include argument
)

sb.glue("media_without_text",
  media_obj,
  encoder='display',
  display={'exclude': 'text/plain'} # forward to format_display_data's kwargs
)
```

Like data scraps, these can be retrieved at a later time be accessing the scrap's
`display` attribute. Though usually one will just use Notebook's `reglue` method
(described below).

### `read_notebook` reads one notebook

Reads a Notebook object loaded from the location specified at `path`.
You've already seen how this function is used in the above api call examples,
but essentially this provides a thin wrapper over an `nbformat`'s NotebookNode
with the ability to extract scrapbook scraps.

```python
nb = sb.read_notebook('notebook.ipynb')
```

This Notebook object adheres to the [nbformat's json schema](https://github.com/jupyter/nbformat/blob/master/nbformat/v4/nbformat.v4.schema.json),
allowing for access to its required fields.

```python
nb.cells # The cells from the notebook
nb.metadata
nb.nbformat
nb.nbformat_minor
```

There's a few additional methods provided, most of which are outlined in more detail
below:

```python
nb.scraps
nb.reglue
```

The abstraction also makes saved content available as a dataframe referencing each
key and source. More of these methods will be made available in later versions.

```python
# Produces a data frame with ["name", "data", "encoder", "display", "filename"] as columns
nb.scrap_dataframe # Warning: This might be a large object if data or display is large
```

The Notebook object also has a few legacy functions for backwards compatibility
with papermill's Notebook object model. As a result, it can be used to read
papermill execution statistics as well as scrapbook abstractions:

```python
nb.cell_timing # List of cell execution timings in cell order
nb.execution_counts # List of cell execution counts in cell order
nb.papermill_metrics # Dataframe of cell execution counts and times
nb.papermill_record_dataframe # Dataframe of notebook records (scraps with only data)
nb.parameter_dataframe # Dataframe of notebook parameters
nb.papermill_dataframe # Dataframe of notebook parameters and cell scraps
```

The notebook reader relies on [papermill's registered iorw](https://papermill.readthedocs.io/en/latest/reference/papermill-io.html)
to enable access to a variety of sources such as -- but not limited to -- S3,
Azure, and Google Cloud.

### `scraps` provides a name -> scrap lookup

The `scraps` method allows for access to all of the scraps in a particular notebook.

```python
nb = sb.read_notebook('notebook.ipynb')
nb.scraps # Prints a dict of all scraps by name
```

This object has a few additional methods as well for convenient conversion and
execution.

```python
nb.scraps.data_scraps # Filters to only scraps with `data` associated
nb.scraps.data_dict # Maps `data_scraps` to a `name` -> `data` dict
nb.scraps.display_scraps # Filters to only scraps with `display` associated
nb.scraps.display_dict # Maps `display_scraps` to a `name` -> `display` dict
nb.scraps.dataframe # Generates a dataframe with ["name", "data", "encoder", "display"] as columns
```

These methods allow for simple use-cases to not require digging through model
abstractions.

### `reglue` copys a scrap into the current notebook

Using `reglue` one can take any scrap glue'd into one notebook and glue into the
current one.

```python
nb = sb.read_notebook('notebook.ipynb')
nb.reglue("table_scrap") # This copies both data and displays
```

Any data or display information will be copied verbatim into the currently
executing notebook as though the user called `glue` again on the original source.

It's also possible to rename the scrap in the process.

```python
nb.reglue("table_scrap", "old_table_scrap")
```

And finally if one wishes to try to reglue without checking for existence the
`raise_on_missing` can be set to just display a message on failure.

```python
nb.reglue("maybe_missing", raise_on_missing=False)
# => "No scrap found with name 'maybe_missing' in this notebook"
```

### `read_notebooks` reads many notebooks

Reads all notebooks located in a given `path` into a Scrapbook object.

```python
# create a scrapbook named `book`
book = sb.read_notebooks('path/to/notebook/collection/')
# get the underlying notebooks as a list
book.notebooks # Or `book.values`
```

The path reuses [papermill's registered `iorw`](https://papermill.readthedocs.io/en/latest/reference/papermill-io.html)
to list and read files form various sources, such that non-local urls can load data.

```python
# create a scrapbook named `book`
book = sb.read_notebooks('s3://bucket/key/prefix/to/notebook/collection/')
```

The Scrapbook (`book` in this example) can be used to recall all scraps across
the collection of notebooks:

```python
book.notebook_scraps # Dict of shape `notebook` -> (`name` -> `scrap`)
book.scraps # merged dict of shape `name` -> `scrap`
```

### `scraps_report` displays a report about collected scraps

The Scrapbook collection can be used to generate a `scraps_report` on all the
scraps from the collection as a markdown structured output.

```python
book.scraps_report()
```

This display can filter on scrap and notebook names, as well as enable or disable
an overall header for the display.

```python
book.scraps_report(
  scrap_names=["scrap1", "scrap2"],
  notebook_names=["result1"], # matches `/notebook/collections/result1.ipynb` pathed notebooks
  header=False
)
```

By default the report will only populate with visual elements. To also
report on data elements set include_data.

```python
book.scraps_report(include_data=True)
```

### papermill support

Finally the scrapbook provides two backwards compatible features for deprecated
`papermill` capabilities:

```python
book.papermill_dataframe
book.papermill_metrics
```

## Encoders

Encoders are accessible by key names to Encoder objects registered
against the `encoders.registry` object. To register new data encoders
simply call:

```python
from encoder import registry as encoder_registry
# add encoder to the registry
encoder_registry.register("custom_encoder_name", MyCustomEncoder())
```

The encode class must implement two methods, `encode` and `decode`:

```python
class MyCustomEncoder(object):
    def encode(self, scrap):
        # scrap.data is any type, usually specific to the encoder name
        pass  # Return a `Scrap` with `data` type one of [None, list, dict, *six.integer_types, *six.string_types]

    def decode(self, scrap):
        # scrap.data is one of [None, list, dict, *six.integer_types, *six.string_types]
        pass  # Return a `Scrap` with `data` type as any type, usually specific to the encoder name
```

This can read transform scraps into a json object representing their contents or
location and load those strings back into the original data objects.

### `text`

A basic string storage format that saves data as python strings.

```python
sb.glue("hello", "world", "text")
```

### `json`

```python
sb.glue("foo_json", {"foo": "bar", "baz": 1}, "json")
```

### `pandas`

```python
sb.glue("pandas_df",pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]}), "pandas")
```

## papermill's deprecated `record` feature

**scrapbook** provides a robust and flexible recording schema. This library replaces [papermill](https://papermill.readthedocs.io)'s existing
`record` functionality.

[Documentation for papermill `record`](https://papermill.readthedocs.io/en/latest/usage-recording.html?#recording-values-to-the-notebook) exists on ReadTheDocs.
In brief, the deprecated `record` function:

`pm.record(name, value)`: enables values to be saved
with the notebook [[API documentation]](https://papermill.readthedocs.io/en/latest/reference/papermill.html#papermill.api.record)

```python
pm.record("hello", "world")
pm.record("number", 123)
pm.record("some_list", [1, 3, 5])
pm.record("some_dict", {"a": 1, "b": 2})
```

`pm.read_notebook(notebook)`: pandas could be used later to recover recorded
values by reading the output notebook into a dataframe. For example:

```python
nb = pm.read_notebook('notebook.ipynb')
nb.dataframe
```

### Rationale for Papermill `record` deprecation

Papermill's `record` function was deprecated due to these limitations and challenges:

- The `record` function didn't follow papermill's pattern of linear execution
  of a notebook. It was awkward to describe `record` as an additional
  feature of papermill, and really felt like describing a second less
  developed library.
- Recording / Reading required data translation to JSON for everything. This is
  a tedious, painful process for dataframes.
- Reading recorded values into a dataframe would result in unintuitive dataframe
  shapes.
- Less modularity and flexiblity than other papermill components where custom
  operators can be registered.

To overcome these limitations in Papermill, a decision was made to create
**Scrapbook**.
