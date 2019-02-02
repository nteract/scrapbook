#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
from os import path
from setuptools import setup

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

python_2 = sys.version_info[0] == 2


def read(fname):
    with open(fname, "rU" if python_2 else "r") as fhandle:
        return fhandle.read()


local_path = os.path.dirname(__file__)
# Fix for tox which manipulates execution pathing
if not local_path:
    local_path = "."


def version():
    with open(local_path + "/scrapbook/version.py", "r") as ver:
        for line in ver.readlines():
            if line.startswith("version ="):
                return line.split(" = ")[-1].strip()[1:-1]
    raise ValueError("No version found in scrapbook/version.py")


req_path = os.path.join(os.path.dirname("__file__"), "requirements.txt")
required = [req.strip() for req in read(req_path).splitlines() if req.strip()]

test_req_path = os.path.join(os.path.dirname("__file__"), "requirements-dev.txt")
test_required = [req.strip() for req in read(test_req_path).splitlines() if req.strip()]
extras_require = {"test": test_required, "dev": test_required}

pip_too_old = False
pip_message = ""

try:
    import pip

    pip_version = tuple([int(x) for x in pip.__version__.split(".")[:3]])
    pip_too_old = pip_version < (9, 0, 1)
    if pip_too_old:
        # pip is too old to handle IPython deps gracefully
        pip_message = (
            "Your pip version is out of date. Papermill requires pip >= 9.0.1. \n"
            "pip {} detected. Please install pip >= 9.0.1.".format(pip.__version__)
        )
except ImportError:
    pip_message = (
        "No pip detected; we were unable to import pip. \n"
        "To use papermill, please install pip >= 9.0.1."
    )
except Exception:
    pass

if pip_message:
    print(pip_message, file=sys.stderr)
    sys.exit(1)


# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scrapbook",
    version=version(),
    description="A library for recording and reading data in Jupyter and nteract Notebooks",
    author="nteract contributors",
    author_email="nteract@googlegroups.com",
    license="BSD",
    # Note that this is a string of words separated by whitespace, not a list.
    keywords="jupyter mapreduce nteract pipeline notebook",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nteract/scrapbook",
    packages=["scrapbook"],
    install_requires=required,
    extras_require=extras_require,
    project_urls={
        "Funding": "https://nteract.io",
        "Source": "https://github.com/nteract/scrapbook/",
        "Tracker": "https://github.com/nteract/scrapbook/issues",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
    ],
)
