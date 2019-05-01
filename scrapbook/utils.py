# -*- coding: utf-8 -*-
"""
utils.py

Provides the base API calls for scrapbook
"""
import sys
import warnings

from functools import wraps


def is_kernel():
    '''
    Returns True if execution context is inside a kernel
    '''
    in_ipython = False
    in_ipython_kernel = False

    # if IPython hasn't been imported, there's nothing to check
    if 'IPython' in sys.modules:
        from IPython import get_ipython
        ip = get_ipython()
        in_ipython = ip is not None

    if in_ipython:
        in_ipython_kernel = getattr(ip, 'kernel', None) is not None

    return in_ipython_kernel


def no_action_without_kernel(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if not is_kernel():
            warnings.warn(
                "No kernel detected for '{fname}'. No action was taken.".format(
                    fname=f.__name__))
        return f(*args, **kwds)
    return wrapper
