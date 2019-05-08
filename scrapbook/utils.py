import warnings

from functools import wraps

from .version import version as sb_version


def deprecated(version, replacement=None):
    '''
    Warns the user that something is deprecated until `version`.
    '''

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
