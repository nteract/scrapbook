import os

# Work-around for https://github.com/Julian/jsonschema/issues/477
from jsonschema.exceptions import _Error

_Error.__eq__ = object.__eq__
_Error.__ne__ = object.__ne__
_Error.__hash__ = object.__hash__


def get_fixture_path(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", *args)


def get_notebook_path(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", *args)


def get_notebook_dir(*args):
    return os.path.dirname(get_notebook_path(*args))
