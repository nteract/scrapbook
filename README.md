# scrapbook

[![Documentation Status](https://readthedocs.org/projects/nteract-scrapbook/badge/?version=latest)](https://nteract-scrapbook.readthedocs.io/en/latest/?badge=latest)

A library for recording a notebook's data values and reading these recorded data
values at a later time.

**scrapbook** provides a robust and flexible recording schema. This library is
planned to replace [papermill](https://papermill.readthedocs.io)'s existing
`record` functionality.

## Use case

Notebook users may wish to record data produced during a notebook execution.
This recorded data can then be read to be used at a later time or be passed to
another notebook as input.

## papermill's record feature

### Background

[Documentation for papermill record](https://papermill.readthedocs.io/en/latest/usage.html#recording-values-to-the-notebook)
In brief:

`pm.record(name, value)`: enables users the ability to record values to be saved
with the notebook [[API documentation]](https://papermill.readthedocs.io/en/latest/reference/papermill.html#papermill.api.record)

```python
pm.record("hello", "world")
pm.record("number", 123)
pm.record("some_list", [1, 3, 5])
pm.record("some_dict", {"a": 1, "b": 2})
```

`pm.read_notebook(notebook)`: pandas can be used later to recover recorded values by reading the output notebook into a dataframe.

```python
nb = pm.read_notebook('notebook.ipynb')
nb.dataframe
```

### Limitations and challenges

- The `record` function doesn't follow papermill's pattern of linear execution
  of a notebook codebase. (It was awkward to describe `record` as an additional
  feature of papermill this week. It really felt like describing a second less 
  developed library.)
- Recording / Reading requires data translation to JSON for everything. This is
  a tedious, painful process for dataframes.
- Reading recorded values into a dataframe may result in unexpected dataframe
  shapes.
- Less modularity and flexiblity than other papermill components where custom
  operators can be registered. (hard to do cross notebook?)

## scrapbook

*Under active design and development. Functionality may change.*

### Ideas and possible approaches for development

- Consider Apache Arrow for dataframe-like saves
- Continue accepting JSON save format (backwards compatibility) 
- Support some other binary forms (plug and play options?)
- Support other standard storage forms as plug and play options, like pandas
  does (Use pandas conversion metaphors as plugins as pandas' implementation is
  a nice feature.)
- Review viability of some of the other data transport ideas between kernels and
  components from elsewhere. nteract??
- Think a little more about secondary language support (R is nice, but we'd want
  support in many languages for the most common transports.)

## Documentation

[Documentation on ReadTheDocs](https://nteract-scrapbook.readthedocs.io/en/latest/)

[API and module reference](https://nteract-scrapbook.readthedocs.io/en/latest/reference/modules.html)
