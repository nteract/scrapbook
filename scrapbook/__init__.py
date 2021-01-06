from __future__ import absolute_import, division, print_function

from .version import version as __version__

from .api import glue, read_notebook, read_notebooks

import warnings
warnings.warn("'nteract-scrapbook' package has been renamed to `scrapbook`. No new releases are going out for this old package name.", FutureWarning)
