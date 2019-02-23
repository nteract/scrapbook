.. _glue_usage:

glue API
========

The ``glue`` call records a :ref:`scrap_model` (data or display value)
in the given notebook cell.

The ``scrap`` (recorded value) can be retrieved during later inspection
of the output notebook.

.. code:: python

    import scrapbook as sb

    sb.glue("hello", "world")
    sb.glue("number", 123)
    sb.glue("some_list", [1, 3, 5])
    sb.glue("some_dict", {"a": 1, "b": 2})
    sb.glue("non_json", df, 'arrow')

The scrapbook library can be used later to recover scraps (recorded
values) from the output notebook:

.. code:: python

    nb = sb.read_notebook('notebook.ipynb')
    nb.scraps

**scrapbook** will imply the storage format by the value type of any
registered data encoders. Alternatively, the implied encoding format can
be overwritten by setting the ``encoder`` argument to the registered
name (e.g. ``"json"``) of a particular encoder.

This data is persisted by generating a display output with a special
media type identifying the content encoding format and data. These
outputs are not always visible in notebook rendering but still exist in
the document. Scrapbook can then rehydrate the data associated with the
notebook in the future by reading these cell outputs.

Display Outputs
---------------

To display a named scrap with visible display outputs, you need to
indicate that the scrap is directly renderable.

This can be done by toggling the ``display`` argument.

.. code:: python

    # record a UI message along with the input string
    sb.glue("hello", "Hello World", display=True)

The call will save the data and the display attributes of the Scrap
object, making it visible as well as encoding the original data. This
leans on the ``IPython.core.formatters.format_display_data`` function to
translate the data object into a display and metadata dict for the
notebook kernel to parse.

Another pattern that can be used is to specify that **only the display
data** should be saved, and not the original object. This is achieved by
setting the encoder to be ``display``.

.. code:: python

    # record an image without the original input object
    sb.glue("sharable_png",
      IPython.display.Image(filename="sharable.png"),
      encoder='display'
    )

Finally the media types that are generated can be controlled by passing
a list, tuple, or dict object as the display argument.

.. code:: python

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

Like data scraps, these can be retrieved at a later time be accessing
the scrap's ``display`` attribute. Though usually one will just use
Notebook's ``reglue`` method (:ref:`notebook_reglue`).
