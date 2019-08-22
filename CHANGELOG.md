# Change Log

## 0.3.1

- Adjusted python 2.7 sci-kit requirements

## 0.3.0

- Added a warning for gluing an object outside of a kernel context
- Added development guide and marked papermill specific functions as deprecated
- Changed error when using GET parameters on cloud storage paths to a warning for non-ipynb extensions
- Changed ipython import to be lazy, saving on initial import times

## 0.2.1

- Fixed reading string json elements from notebook store (needed to read strings saved with papermill.record)

## 0.2.0

- Added schema versions to media payloads
- Overhaul of internal modules based on interactive feedback at NES
- Docs are now fully covering capabilities
- Binder links fixed

## 0.1.0

- Initial Release!
