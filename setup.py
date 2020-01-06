#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from os import path
from setuptools import setup


def read(fname):
    with open(fname, "r") as fhandle:
        return fhandle.read()


local_path = os.path.dirname(__file__)
# Fix for tox which manipulates execution pathing
if not local_path:
    local_path = "."
here = path.abspath(path.dirname(__file__))


def version():
    with open(local_path + "/scrapbook/version.py", "r") as ver:
        for line in ver.readlines():
            if line.startswith("version ="):
                return line.split(" = ")[-1].strip()[1:-1]
    raise ValueError("No version found in scrapbook/version.py")


def read_reqs(fname):
    req_path = os.path.join(here, fname)
    return [req.strip() for req in read(req_path).splitlines() if req.strip()]


reqs_s3 = ["papermill[s3]"]
reqs_azure = ["papermill[azure]"]
reqs_gcs = ["papermill[gcs]"]
reqs_all = ["papermill[all]"]
reqs_dev = read_reqs("requirements-dev.txt")
extras_require = {
    "test": reqs_dev,
    "dev": reqs_dev,
    "all": reqs_all,
    "s3": reqs_s3,
    "azure": reqs_azure,
    "gcs": reqs_gcs,
}

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nteract-scrapbook",
    version=version(),
    description="A library for recording and reading data in Jupyter and nteract Notebooks",
    author="nteract contributors",
    author_email="nteract@googlegroups.com",
    license="BSD",
    keywords=["jupyter", "mapreduce", "nteract", "pipeline", "notebook"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nteract/scrapbook",
    packages=["scrapbook"],
    python_requires='>=3.5',
    include_package_data=True,
    install_requires=read_reqs("requirements.txt"),
    extras_require=extras_require,
    project_urls={
        "Documentation": "https://nteract-scrapbook.readthedocs.io",
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
