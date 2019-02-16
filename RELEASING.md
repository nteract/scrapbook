# Releasing

## Pre-requisites

- First check that the CHANGELOG is up to date for the next release version
- Ensure dev requirements are installed `pip install .[dev]`

## Push to github

```bash
bumpversion patch
git push && git push --tags
```

## Push to PyPi

```bash
rm -rf dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```
