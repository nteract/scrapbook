# Development Guide

_Note: Please read the CONTRIBUTING.md instructions, before continuing._

This document outlines the various mechanisms within the repo and how they function. This is intended to help with development and code review processes and to add context for less familiar developers.

_Warning: The contracts below and their roles are subject to moderate changes until a 1.0 roadmap / release is reached._

## How Data Is Persisted

When data is saved by scrapbook it relies on encapsulating data within display outputs that get persisted by kernel clients. In the notebook case this means saved as outputs in the node's `nb.cell.outputs` in a special format. Later on these outputs are collected and extracted by looking for the contract format specified by scrapbook.

### Encoded Data

When saving encoded data, display outputs are persisted with a media type of `application/scrapbook.scrap.<encoder>+json`. This media type is not (currently) intended to be rendered and is kept separate from the `display` data content and media type. The `application/scrapbook.scrap` data is the json representation of the scrap's data contents passed into `glue` function calls. Its stored contents is persisted in the `scrapbook/schemas/scrap.<version>.json` format to enable extraction and recall of the in-memory data model at a later time.

### Display Data

Unlike encoded data, pure display data such as graphs, text, or images are displayed as though `ipython.display(scrap)` were called. Except that the metadata of the saved object has an additional `"scrapbook"` dictionary of the shape `{"name": name, "data": False, "display": True}`. This is done for two reason. First, the `scrap` is rendered in the browser while still being retrievable by name. And second, to avoid duplicating potentially large objects in both the display and data outputs. When a notebook is read it combines the display data back with any associated encoded data with the same name.

## API Contracts

Effectively the repo splits code execution into two groups: (re)writing data in notebooks and extracting data from notebooks. The former group uses the `glue` mechanism to attach data to a notebook while the `read_notebook(s)` mechanisms enable recall in the latter group. The data model `glue` generates and `read_notebook` rehydrates is a `scrap`, which follows a schema defined in `scrapbook/schemas/scrap.<version>.json`.

### `glue` / `reglue`

When executing from within a kernel, the `glue` function converts data into display outputs that can be persisted within a notebook, or other json storage format. For the sake of simplicity we'll just refer to this pattern in reference to the notebook usecase, with the knowledge that one could use it in any kernel execution context.

The `reglue` function is simply a mechanism for transferring `glue`ed data into a new notebook. Operationally it needs fewer controls because the context of storage and persistence is already encapsulated in the original `scrap`.

#### `name`

The name to persist data against. If a `glue` operation is repeated with the same `name`, reads will ignore earlier saved values.

#### `scrap`

The raw data to persist in the notebook. If the `scrap` type / contents can't be persisted an exception will be thrown by the encoder handler.

#### `encoder`

The `encoder` specifies the handler type which is used to translate python objects into a format that can be saved within a notebook. The named encoder is responsible for ensuring that data can be transformed bidirectionally in a best-effort for accuracy. Times when this cannot be perfectly guaranteed usually involve floating point rounding or complex class transformations.

Assigning `encoder` to the value of `"display"` is a special assignment which will cause the scrap data to only persist display results and not persist any raw data. This assignment defaults the `display` argument to be `True` if not provided.

#### `display`

The display option provides two capabilities to data persistence in parallel to data saved with the given `encoder`. This display content is saved under the same `name` without replacing and raw data of the scrap.

First, if the option is truthy it will cause the `scrap`'s IPython display media types to be saved as display data. For example, if an IPython `Image` object is the scrap in question then a truthy display would persist the html and text media type responses in the notebook under the `name` key.

Second, if the `display` argument is a `list` or `dict` then it is tranlated into arguments to `IPython.core.formatters.format_display_data`. In the `list` case it translates the argument into the `"include"` kwarg value. In the `dict` case it maps the argument directly to the kwargs of the function call.

This enables callers to control the display output bound to the `name` when they want full control of execution, but also lets users easily indicate they want a normal display mapped to the scrap `name`.

### `read_notebook` -> `Notebook`

Whenever a caller wishes to extract data from a notebook which has already executed, they will end up calling the `read_notebook` function and extracting the `scraps` through one of a variety of helper methods. The read operation returns a `Notebook` object which is a superset of the `nbformat` schema'd notebook model in order to allow notebook access patterns of related libraries while enabling scrapbook specific function calls.

#### `scraps`

A property which recalls all of the `Scrap` objects persisted in the notebook as a collection. This collection is keyed the the `name` of data and displays. The majority of the remaining `Notebook` public functions are based off this property's results.

Older scrap versions, including `papermill`'s `record` model (treated as v0), are translated to the latest version schema in this process. Thus backwards compatibility is preserved despite library version differences between reader and consumer so long as the reader is a later release. In violation of this pattern, a best effort is made to read later versions, though exceptions may be raised for severe incompatibilities.

#### `papermill` Backwards Compatibility

Several functions are present which support papermill operations. These will be removed or renamed by the scrapbook 1.0 release. They exist to fulfill the old library contracts which were fully removed in papermill's 1.0 release.

### `read_notebooks` -> `Scrapbook`

The `read_notebooks` function is very similar to the singular `read_notebook` call, except that it wraps several notebook read operations in one `Scrapbook` collection object. This object has additional useful methods.

#### `notebook_scraps`

A collection of scraps keyed by the notebook's id (defaulted to file basename) and valued with that notebook's `scraps` collection. This is useful for differentiating the source a particular scrap.

#### `scraps`

A collapsed version of `notebook_scraps` where all of the underlying `scrap` collections are combined by name. Duplicate names discard only respect the last named scrap visited during iteration.

#### `scraps_report`

A function meant purely for reporting purposes. Calling `scraps_report` generates a markdown report for the scraps found across the collection of notebooks loaded. There's several controlling arguments to help with avoiding rendering very large results or to aid in different reporting goals.

#### `papermill` Backwards Compatibility

See `read_notebook` section on the topic.

### `Scraps` Model

The `Scraps` model is a light wrapper on an ordered dict which includes some filtering and conversion helper methods. It's intended to represent a collection of `scrap`s and make other function calls simpler when interacting with these collections.

## Testing

When creating tests for scrapbook there are a few core patterns that should be respected if possible.

### Read from Notebooks

Add scraps with new features to the test notebook files and ensure they can be read from those ipynb files. This is crucial for ensuring that the end-to-end capabilities of scrapbook are preserved and respected in recall. Just testing with pre-generated scrap objects is not sufficient.

### Encoder / Scrap Combinations

When adding encoders, ensure they are tested with a variety of positive and negative encoding cases. The `@pytest.mark.parametrize` decorator is quite helpful for these test patterns.

### Scrapbook Schema Version Changes

Whenever the scrapbook schema changes ensure there are test for older schema payloads, including tests that read from files with the old schema. We want strong guarantees that scrapbook version changes do not break existing execution patterns during version transitions.
