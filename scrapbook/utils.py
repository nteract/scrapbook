# -*- coding: utf-8 -*-
"""
utils.py

Provides the utilities for scrapbook functions and operations.
"""
import sys
import warnings
from functools import wraps


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
            warnings.warn(
                "No kernel detected for '{fname}'.".format(
                    fname=f.__name__))
        return f(*args, **kwds)
    return wrapper
