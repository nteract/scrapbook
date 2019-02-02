import os


def get_fixture_path(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", *args)


def get_notebook_path(*args):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks", *args)


def get_notebook_dir(*args):
    return os.path.dirname(get_notebook_path(*args))
