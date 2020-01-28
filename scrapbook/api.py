# -*- coding: utf-8 -*-
"""
api.py

Provides the base API calls for scrapbook
"""
import os

# We lean on papermill's readers to connect to remote stores
from papermill.iorw import list_notebook_files

from .models import Notebook, Scrapbook
from .scraps import Scrap, scrap_to_payload
from .schemas import GLUE_PAYLOAD_FMT
from .encoders import registry as encoder_registry
from .utils import kernel_required


@kernel_required
def glue(name, data, encoder=None, display=None):
    """
    Records a data value in the given notebook cell.

    The recorded data value can be retrieved during later inspection of the
    output notebook.

    The data type of the scraps is implied by the value type of any of the
    registered data encoders, but can be overwritten by setting the `encoder`
    argument to a particular encoder's registered name (e.g. `"json"`).

    This data is persisted by generating a display output with a special media
    type identifying the content storage encoder and data. These outputs are not
    visible in notebook rendering but still exist in the document. Scrapbook
    then can rehydrate the data associated with the notebook in the future by
    reading these cell outputs.

    Example
    -------

        sb.glue("hello", "world")
        sb.glue("number", 123)
        sb.glue("some_list", [1, 3, 5])
        sb.glue("some_dict", {"a": 1, "b": 2})
        sb.glue("non_json", df, 'arrow')

    The scrapbook library can be used later to recover scraps (recorded values)
    from the output notebook

        nb = sb.read_notebook('notebook.ipynb')
        nb.scraps

    Parameters
    ----------
    name: str
        Name of the value to record.
    data: any
        The value to record. This must be an object for which an encoder's
        `encodable` method returns True.
    encoder: str (optional)
        The name of the handler to use in persisting data in the notebook.
    display: any (optional)
        An indicator for persisting controlling displays for the named record.
    """
    # Keep slow import lazy
    import IPython
    from IPython.display import display as ip_display

    # TODO: Implement the cool stuff. Remote storage indicators?!? Maybe remote media type?!?
    if not encoder:
        try:
            encoder = encoder_registry.determine_encoder_name(data)
        except NotImplementedError:
            if display is not None:
                # Do not raise an exception if the scrap isn't encodable because
                # the corresponding display object may be.
                encoder = 'display'
            else:
                raise

    if display is None:
        display = encoder == "display"

    # Only store data that can be stored (purely display scraps can skip)
    if encoder != "display":
        ipy_data, metadata = _prepare_ipy_data_format(
            name, scrap_to_payload(encoder_registry.encode(Scrap(name, data, encoder))), encoder
        )
        ip_display(ipy_data, metadata=metadata, raw=True)

    # Only display data that is marked for display
    if display:
        display_kwargs = {}
        if isinstance(display, (list, tuple)):
            display_kwargs = {"include": display}
        elif isinstance(display, dict):
            display_kwargs = display
        raw_data, raw_metadata = IPython.core.formatters.format_display_data(data, **display_kwargs)
        data, metadata = _prepare_ipy_display_format(name, raw_data, raw_metadata)
        ip_display(data, metadata=metadata, raw=True)


def _prepare_ipy_data_format(name, payload, encoder):
    data = {GLUE_PAYLOAD_FMT.format(encoder=encoder): payload}
    metadata = {"scrapbook": dict(name=name, data=True, display=False)}
    # We don't display immediately here as this makes mocking difficult
    return data, metadata


def _prepare_ipy_display_format(name, payload, metadata):
    metadata["scrapbook"] = dict(name=name, data=False, display=True)
    # We don't display immediately here as this makes mocking difficult
    return payload, metadata


def read_notebook(path):
    """
    Returns a Notebook object loaded from the location specified at `path`.

    Parameters
    ----------
    path : str
        Path to a notebook `.ipynb` file.

    Returns
    -------
    notebook : object
        A Notebook object.

    """
    return Notebook(path)


def read_notebooks(path):
    """
    Returns a Scrapbook including the notebooks read from the
    directory specified by `path`.

    Parameters
    ----------
    path : str
        Path to directory containing notebook `.ipynb` files.

    Returns
    -------
    scrapbook : object
        A `Scrapbook` object.

    """
    scrapbook = Scrapbook()
    for notebook_path in sorted(list_notebook_files(path)):
        fn = os.path.splitext(os.path.basename(notebook_path))[0]
        scrapbook[fn] = read_notebook(notebook_path)
    return scrapbook
