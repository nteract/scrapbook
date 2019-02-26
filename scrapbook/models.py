# -*- coding: utf-8 -*-
"""
models.py

Provides the various model wrapper objects for scrapbook
"""
from __future__ import unicode_literals
import os
import copy
import nbformat
import collections
import pandas as pd

from six import string_types
from collections import OrderedDict
from IPython.display import display as ip_display, Markdown

# We lean on papermill's readers to connect to remote stores
from papermill.iorw import papermill_io

from .scraps import Scrap, Scraps, payload_to_scrap, scrap_to_payload
from .schemas import GLUE_PAYLOAD_PREFIX, RECORD_PAYLOAD_PREFIX
from .encoders import registry as encoder_registry
from .exceptions import ScrapbookException


def merge_dicts(dicts):
    iterdicts = iter(dicts)
    outcome = next(iterdicts).copy()
    for d in iterdicts:
        outcome.update(d)
    return outcome


class Notebook(object):
    """
    Representation of a notebook. This model is quasi-compatible with the
    nbformat NotebookNode object in that it support access to the v4
    required fields from nbformat's json schema. For complete access to
    normal nbformat operations, use the `node` attribute of this model.

    Parameters
    ----------
    node_or_path : `nbformat.NotebookNode`, str
        a notebook object, or a path to a notebook object
    """

    def __init__(self, node_or_path):
        if isinstance(node_or_path, string_types):
            if not node_or_path.endswith(".ipynb"):
                raise ValueError(
                    "Requires an '.ipynb' file extension. Provided path: '{}'".format(
                        node_or_path
                    )
                )
            self.path = node_or_path
            self.node = nbformat.reads(papermill_io.read(node_or_path), as_version=4)
        else:
            self.path = ""
            self.node = node_or_path

        # Memoized traits
        self._scraps = None
        self._outputs = None

    def copy(self):
        cp = Notebook(self.node.copy())
        cp.path = self.path
        return cp

    # nbformat mirroring properties
    @property
    def metadata(self):
        return self.node.metadata

    @property
    def nbformat_minor(self):
        return self.node.nbformat_minor

    @property
    def nbformat(self):
        return self.node.nbformat

    @property
    def cells(self):
        return self.node.cells

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
        return self.metadata.get("papermill", {}).get("parameters", {})

    def _extract_papermill_output_data(self, sig, payload):
        if sig.startswith(RECORD_PAYLOAD_PREFIX):
            # Fetch '+json' and strip the leading '+'
            encoder = sig.split(RECORD_PAYLOAD_PREFIX, 1)[1][1:]
            # First key is the only named payload
            for name, data in payload.items():
                return encoder_registry.decode(Scrap(name, data, encoder))

    def _extract_output_data_scraps(self, output):
        output_scraps = Scraps()
        for sig, payload in output.get("data", {}).items():
            # Backwards compatibility for papermill
            scrap = self._extract_papermill_output_data(sig, payload)
            if scrap is None and sig.startswith(GLUE_PAYLOAD_PREFIX):
                scrap = encoder_registry.decode(payload_to_scrap(payload))
            if scrap:
                output_scraps[scrap.name] = scrap

        return output_scraps

    def _extract_output_displays(self, output):
        output_displays = OrderedDict()
        # Backwards compatibility for papermill
        metadata = output.get("metadata", {})
        if "papermill" in metadata:
            output_name = output.metadata["papermill"].get("name")
            if output_name:
                output_displays[output_name] = output
        # Only grab outputs that are displays
        elif metadata.get("scrapbook", {}).get("display"):
            output_name = output.metadata["scrapbook"].get("name")
            if output_name:
                output_displays[output_name] = output

        return output_displays

    def _fetch_scraps(self):
        """Returns a dictionary of the data recorded in a notebook."""
        scraps = Scraps()

        for cell in self.cells:
            for output in cell.get("outputs", []):
                output_data_scraps = self._extract_output_data_scraps(output)
                output_displays = self._extract_output_displays(output)

                # Combine displays with data while trying to preserve ordering
                output_scraps = Scraps(
                    [
                        # Hydrate with output_displays
                        (
                            scrap.name,
                            Scrap(
                                scrap.name,
                                scrap.data,
                                scrap.encoder,
                                output_displays.get(scrap.name),
                            ),
                        )
                        for scrap in output_data_scraps.values()
                    ]
                )
                for name, display in output_displays.items():
                    if name not in output_scraps:
                        output_scraps[name] = Scrap(name, None, "display", display)
                scraps.update(output_scraps)

        return scraps

    @property
    def scraps(self):
        """dict: a dictionary of data found in the notebook"""
        if self._scraps is None:
            self._scraps = self._fetch_scraps()
        return self._scraps

    @property
    def cell_timing(self):
        """list: a list of cell execution timings in cell order"""
        return [
            # TODO: Other timing conventions?
            cell.metadata.get("papermill", {}).get("duration", 0.0)
            if cell.get("execution_count")
            else None
            for cell in self.cells
        ]

    @property
    def execution_counts(self):
        """list: a list of cell execution counts in cell order"""
        return [cell.get("execution_count") for cell in self.cells]

    @property
    def papermill_metrics(self):
        """pandas dataframe: dataframe of cell execution counts and times"""
        df = pd.DataFrame(columns=["filename", "cell", "value", "type"])

        for i, cell in enumerate(self.cells):
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
        df = self.scraps.dataframe
        df["filename"] = self.filename
        return df

    @property
    def papermill_record_dataframe(self):
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
        return self.parameter_dataframe.append(
            self.papermill_record_dataframe, ignore_index=True
        )

    def _strip_scrapbook_metadata(self, metadata):
        copied = copy.copy(metadata)
        # Strip old metadata name
        copied.pop("papermill", None)
        copied.pop("scrapbook", None)
        return copied

    def reglue(self, name, new_name=None, raise_on_missing=True, unattached=False):
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
        unattached : bool
            indicator for rendering without making the display recallable as scrapbook data
        """
        # Avoid circular imports
        from .api import _prepare_ipy_data_format, _prepare_ipy_display_format

        if name not in self.scraps:
            if raise_on_missing:
                raise ScrapbookException(
                    "Scrap '{}' is not available in this notebook.".format(name)
                )
            else:
                ip_display(
                    "No scrap found with name '{}' in this notebook".format(name)
                )
        else:
            scrap = self.scraps[name]
            if new_name:
                scrap = scrap._replace(name=new_name)
            if scrap.data is not None:
                data, metadata = _prepare_ipy_data_format(
                    scrap.name, scrap_to_payload(scrap), scrap.encoder
                )
                # Skip saving data for later regluing and remove 'scrapbook'
                # from keys, when unattached
                if unattached:
                    metadata = self._strip_scrapbook_metadata(metadata)
                ip_display(data, metadata=metadata, raw=True)
            if scrap.display is not None:
                scrap_data = scrap.display.get("data", {})
                scrap_metadata = self._strip_scrapbook_metadata(
                    scrap.display.get("metadata", {})
                )
                data, metadata = _prepare_ipy_display_format(
                    scrap.name, scrap_data, scrap_metadata
                )
                if unattached:
                    # Remove 'scrapbook' from keys if we want it unassociated
                    metadata = self._strip_scrapbook_metadata(metadata)
                ip_display(data, metadata=metadata, raw=True)


class Scrapbook(collections.MutableMapping):
    """
    A collection of notebooks represented as a dictionary of notebooks
    """

    def __init__(self):
        self._notebooks = OrderedDict()

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
        return self.values()

    @property
    def notebook_scraps(self):
        """dict: a dictionary of the notebook scraps by key."""
        return OrderedDict([(key, nb.scraps) for key, nb in self._notebooks.items()])

    @property
    def scraps(self):
        """dict: a dictionary of the merged notebook scraps."""
        return Scraps(merge_dicts(nb.scraps for nb in self.notebooks))

    def scraps_report(
        self, scrap_names=None, notebook_names=None, include_data=False, headers=True
    ):
        """
        Display scraps as markdown structed outputs.

        Parameters
        ----------
        scrap_names : str or iterable[str] (optional)
            the scraps to display as reported outputs
        notebook_names : str or iterable[str] (optional)
            notebook names to use in filtering on scraps to report
        include_data : bool (default: False)
            indicator that data-only scraps should be reported
        header : bool (default: True)
            indicator for if the scraps should render with a header
        """

        def trim_repr(data):
            # Generate a small data representation for display purposes
            if not isinstance(data, string_types):
                data_str = repr(data)
            if len(data_str) > 102:
                data_str = data_str[:100] + "..."
            return data_str

        if isinstance(scrap_names, string_types):
            scrap_names = [scrap_names]
        scrap_names = set(scrap_names or [])

        if notebook_names is None:
            notebook_names = self._notebooks.keys()
        elif isinstance(notebook_names, string_types):
            notebook_names = [notebook_names]

        for i, nb_name in enumerate(notebook_names):
            notebook = self[nb_name]
            if headers:
                if i > 0:
                    ip_display(Markdown("<hr>"))  # tag between outputs
                ip_display(Markdown("### {}".format(nb_name)))

            for name in scrap_names or notebook.scraps.display_scraps.keys():
                if headers:
                    ip_display(Markdown("#### {}".format(name)))
                notebook.reglue(name, raise_on_missing=False, unattached=True)

            if include_data:
                for name, scrap in scrap_names or notebook.scraps.data_scraps.items():
                    if scrap.display is None and scrap.data is not None:
                        if headers:
                            ip_display(Markdown("#### {}".format(name)))
                            ip_display(trim_repr(scrap.data))
                        else:
                            ip_display(
                                "{}: {}".format(scrap.name, trim_repr(scrap.data))
                            )
