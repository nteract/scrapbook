# -*- coding: utf-8 -*-
"""
notebook.py

Provides the Notebook wrapper objects for scrapbook
"""
from __future__ import unicode_literals
import os
import copy
import operator
import collections
import pandas as pd

from six import string_types
from collections import namedtuple
from IPython.display import display as ip_display, Markdown

# We lean on papermill's readers to connect to remote stores
from papermill.iorw import load_notebook_node

from .translators import registry as translator_registry
from .exceptions import ScrapbookException


GLUE_OUTPUT_PREFIX = "application/scrapbook.scrap+"
RECORD_OUTPUT_PREFIX = "application/papermill.record+"
DATA_OUTPUT_PREFIXES = [
    GLUE_OUTPUT_PREFIX,
    RECORD_OUTPUT_PREFIX,  # Backwards compatibility
]


def merge_dicts(dicts):
    iterdicts = iter(dicts)
    outcome = next(iterdicts).copy()
    for d in iterdicts:
        outcome.update(d)
    return outcome


Scrap = namedtuple('Scrap', ['name', 'data', 'storage', 'display'])


class Scraps(collections.OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Scraps, self).__init__(*args, **kwargs)

    def data_scraps(self):
        return collections.OrderedDict([(
            k, v for k, v in self if v.data is not None)])

    def display_scraps(self):
        return collections.OrderedDict([(
            k, v for k, v in self if v.display is not None)])


# TODO: Inherit from nbformat
class Notebook(object):
    """
    Representation of a notebook.

    Parameters
    ----------
    node : `nbformat.NotebookNode`, str
        a notebook object, or a path to a notebook object
    """

    def __init__(self, node_or_path, translators=None):
        if isinstance(node_or_path, string_types):
            if not node_or_path.endswith(".ipynb"):
                raise ValueError(
                    "Requires an '.ipynb' file extension. Provided path: '{}'".format(
                        node_or_path
                    )
                )
            self.path = node_or_path
            self.node = load_notebook_node(node_or_path)
        else:
            self.path = ""
            self.node = node_or_path
        self.translators = translators or translator_registry

        # Memoized traits
        self._scraps = None
        self._outputs = None

    @property
    def filename(self):
        """str: filename found a the specified path"""
        return os.path.basename(self.path)

    @property
    def directory(self):
        """str: directory name found for a notebook (nb)"""
        return os.path.dirname(self.path)

    @property
    def parameters(self):
        """dict: parameters stored in the notebook metadata"""
        return self.node.metadata.get("papermill", {}).get("parameters", {})

    def _extract_output_data(self, output):
        output_data = collections.OrderedDict()
        for sig, payload in output.get("data", {}).items():
            # Backwards compatibility for papermill
            for prefix in DATA_OUTPUT_PREFIXES:
                if sig.startswith(prefix):
                    for name, data in payload.items():
                        format = sig.split(prefix, 1)[1]
                        output_data[(name, format)] = self.translators.load_data(
                            name, format, data
                        )

        return output_data

    def _extract_output_displays(self, output):
        output_displays = collections.OrderedDict()
        # Backwards compatibility for papermill
        for namespace in ["scrapbook", "papermill"]:
            if namespace in output.get("metadata", {}):
                output_name = output.metadata[namespace].get("name")
                if output_name:
                    output_displays[output_name] = output
                    break

        return output_displays

    def _fetch_scraps(self):
        """Returns a dictionary of the data recorded in a notebook."""
        scraps = Scraps()

        for cell in self.node.cells:
            for output in cell.get("outputs", []):
                output_data = _extract_output_data(output)
                output_displays = _extract_output_displays(output)

                # Combine displays with data while trying to preserve ordering
                output_scraps = Scraps([
                    (name, Scrap(name, data, format, output_displays.get(name)))
                    for (name, format), data in output_data.items()
                ])
                for name, display in output_displays.items():
                    if name not in output_scraps:
                        output_scraps[name] = Scrap(name, None, 'display', display)
                scraps.update(output_scraps)

        return scraps

    @property
    def scraps(self):
        """dict: a dictionary of data found in the notebook"""
        if self._scraps is None:
            self._scraps = self._fetch_scraps()
        return self._scraps

    def _output_is_scrap(self, output):
        for sig, payload in output.get("data", {}).items():
            # Backwards compatibility for papermill
            if any(sig.startswith(prefix) for prefix in DATA_OUTPUT_PREFIXES):
                return True
        for namespace in ["scrapbook", "papermill"]:
            if namespace in output.get("metadata", {}):
                return True
        return False

    def _fetch_raw_outputs:
        outputs = []
        for cell in self.node.cells:
            for output in cell.get("outputs", []):
                if self._output_is_scrap(output):
                    outputs.append(output)
        return outputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = self._fetch_raw_outputs()
        return self._outputs

    @property
    def cell_timing(self):
        """list: a list of cell execution timings in cell order"""
        return [
            # TODO: Other timing conventions?
            cell.metadata.get("papermill", {}).get("duration", 0.0)
            if cell.get("execution_count")
            else None
            for cell in self.node.cells
        ]

    @property
    def execution_counts(self):
        """list: a list of cell execution counts in cell order"""
        return [cell.get("execution_count") for cell in self.node.cells]

    @property
    def papermill_metrics(self):
        """pandas dataframe: dataframe of cell execution counts and times"""
        df = pd.DataFrame(columns=["filename", "cell", "value", "type"])

        for i, cell in enumerate(self.node.cells):
            execution_count = cell.get("execution_count")
            if not execution_count:
                continue
            name = "Out [{}]".format(str(execution_count))
            value = cell.metadata.get("papermill", {}).get("duration", 0.0)
            df.loc[i] = self.filename, name, value, "time (s)"
        return df

    @property
    def parameter_dataframe(self):
        """pandas dataframe: dataframe of notebook parameters"""
        # Meant for backwards compatibility to papermill's dataframe method
        return pd.DataFrame(
            [
                [name, self.parameters[name], "parameter", self.filename]
                for name in sorted(self.parameters.keys())
            ],
            columns=["name", "value", "type", "filename"],
        )

    @property
    def scrap_dataframe(self):
        """pandas dataframe: dataframe of cell scraps"""
        # Meant for backwards compatibility to papermill's dataframe method
        return pd.DataFrame(
            [
                [name, self.scraps[name].data, "record", self.filename]
                for name in sorted(self.scraps.keys())
                if self.scraps[name].data is not None
            ],
            columns=["name", "value", "type", "filename"],
        )

    @property
    def papermill_dataframe(self):
        """pandas dataframe: dataframe of notebook parameters and cell scraps"""
        # Meant for backwards compatibility to papermill's dataframe method
        return self.parameter_dataframe.append(self.scrap_dataframe, ignore_index=True)

    def _output_name(self, output):
        # Check metadata
        for namespace in ["scrapbook", "papermill"]:
            if namespace in output.get("metadata", {}):
                output_name = output.metadata[namespace].get("name")
                if output_name:
                    return name

        # Fallback to data
        for sig, payload in output.get("data", {}).items():
            for name in (payload or {}).keys():
                return name

    def _rename_output(self, old_name, new_name, output):
        renamed = copy.copy(output)
        # Strip old metadata name
        renamed.metadata.pop("papermill")
        renamed.metadata["scrapbook"] = output.metadata.get("scrapbook", {})
        renamed.metadata["scrapbook"]["name"] = new_name

        # Update any data available
        if "data" in output and old_name in output["data"]:
            renamed["data"] = copy.copy(renamed["data"])
            renamed["data"][new_name] = renamed["data"].pop(old_name)

        return renamed

    def reglue(self, name, new_name=None, raise_on_missing=True):
        """
        Display output from a named source of the notebook.

        Parameters
        ----------
        name : str
            name of scrap object
        new_name : str
            replacement name for scrap
        raise_error : bool
            indicator for if the resketch should print a message or error on missing snaps

        """
        if name not in self.scraps:
            if raise_on_missing:
                raise ScrapbookException(
                    "Scrap '{}' is not available in this notebook.".format(name)
                )
            else:
                ip_display("No scrap available for {}".format(name))
        else:
            scrap = self.scraps[name]

        for output in self.outputs:
            out_name = self._output_name(name)
            if out_name == name:
                # Always rename to update stale metadata structures
                output = self._rename_output(old_name, new_name or name, output)
                # Call raw display function on output
                ip_display(output.data, metadata=output.metadata, raw=True)


# TODO: Update to just glue
class Scrapbook(collections.MutableMapping):
    """
    A collection of notebooks represented as a dictionary of notebooks
    """

    def __init__(self):
        self._notebooks = collections.OrderedDict()

    def __setitem__(self, key, value):
        # If notebook is a path str then load the notebook.
        if isinstance(value, string_types):
            value = Notebook(value)
        self._notebooks.__setitem__(key, value)

    def __getitem__(self, key):
        return self._notebooks.__getitem__(key)

    def __delitem__(self, key):
        return self._notebooks.__delitem__(key)

    def __iter__(self):
        return self._notebooks.__iter__()

    def __len__(self):
        return self._notebooks.__len__()

    @property
    def papermill_dataframe(self):
        """list: a list of data names from a collection of notebooks"""

        # Backwards compatible dataframe interface

        df_list = []
        for key in self._notebooks:
            nb = self._notebooks[key]
            df = nb.papermill_dataframe
            df["key"] = key
            df_list.append(df)
        return pd.concat(df_list).reset_index(drop=True)

    @property
    def papermill_metrics(self):
        """list: a list of metrics from a collection of notebooks"""
        df_list = []
        for key in self._notebooks:
            nb = self._notebooks[key]
            df = nb.papermill_metrics
            df["key"] = key
            df_list.append(df)
        return pd.concat(df_list).reset_index(drop=True)

    @property
    def notebooks(self):
        """list: a sorted list of associated notebooks."""
        return map(
            operator.itemgetter(1),
            sorted(self._notebooks.items(), key=operator.itemgetter(0)),
        )

    @property
    def scraps(self):
        """dict: a dictionary of the notebook scraps by key."""
        return {key: nb.scraps for key, nb in self._notebooks.items()}

    @property
    def flat_scraps(self):
        """dict: a dictionary of the merged notebook scraps."""
        return merge_dicts(nb.scraps for nb in self.notebooks)

    @property
    def snaps(self):
        """dict: a dictionary of the notebook snap outputs by key."""
        return {key: nb.snaps for key, nb in self._notebooks.items()}

    @property
    def flat_snaps(self):
        """dict: a dictionary of the merged notebook snap outputs."""
        return merge_dicts(nb.snaps for nb in self.notebooks)

    def display(self, snaps=None, keys=None, header=True, raise_error=False):
        """
        Display snaps as markdown structed outputs.

        Parameters
        ----------
        snaps : str or iterable[str] (optional)
            the snaps to display as outputs
        keys : str or iterable[str] (optional)
            notebook keys to use in framing the scrapbook displays
        header : bool (default: True)
            indicator for if the snaps should have headers
        raise_error : bool (default: False)
            flag for if errors should be raised on missing output_names
        """
        if isinstance(snaps, string_types):
            snaps = [snaps]

        if keys is None:
            keys = self._notebooks.keys()
        elif isinstance(keys, string_types):
            keys = [keys]

        for i, k in enumerate(keys):
            if header:
                if i > 0:
                    ip_display(Markdown("<hr>"))  # tag between outputs
                ip_display(Markdown("### {}".format(k)))

            if snaps is None:
                names = self[k].snaps.keys()
            else:
                names = snaps

            for name in names:
                if header:
                    ip_display(Markdown("#### {}".format(name)))
                self[k].resketch(name, raise_error=raise_error)
