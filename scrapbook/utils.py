# -*- coding: utf-8 -*-
"""
utils.py

Provides the utilities for scrapbook functions and operations.
"""
import sys
import warnings
from functools import wraps

from .version import version as sb_version


def deprecated(version, replacement=None):
    """
    Warns the user that something is deprecated. Removal planned in `version` release.
    """

    def wrapper(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            replace_resp = ""
            if replacement:
                replace_resp = (
                    " Please see {replacement} as a replacement for this "
                    "functionality.".format(replacement=replacement)
                )
            warnings.warn(
                "Function {name} is deprecated and will be removed in verison {target} "
                "(current version {current}).{replace_resp}".format(
                    name=func.__name__,
                    target=version,
                    current=sb_version,
                    replace_resp=replace_resp,
                ),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return new_func

    return wrapper


def is_kernel():
    """
    Returns True if execution context is inside a kernel
    """
    # if IPython hasn't been imported, there's nothing to check
    if 'IPython' in sys.modules:
        from IPython import get_ipython

        ipy = get_ipython()
        if ipy is not None:
            return getattr(ipy, 'kernel', None) is not None
    return False


def kernel_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if not is_kernel():
            warnings.warn("No kernel detected for '{fname}'.".format(fname=f.__name__))
        return f(*args, **kwds)

    return wrapper
