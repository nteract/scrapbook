# scrapbook
A library for recording and reading data in notebooks.

This project is intended to replace the record functionality from papermill with a more robust and flexible saving schema. Below is an outline of the objective of this repo and some ideas to drive towards with development.

## Challenges with papermill record today

- Doesn't quite fit with the rest of papermill linear execution codebase (it was awkward to describe it as an additional feature of papermill this week, really felt like describing a second less developed library)
- Requires translation to JSON for everything (dataframes are painful here)
- Reading records into a result dataframe isn't always the shape you'd expect
- Not as modular as other components of papermill where we can register custom operators (hard to do cross notebook?)

## Ideas

- Use arrow for dataframe like saves?
- Still accept JSON (backwards compatibility)
- Some other binary forms (plug and play options?)
- Support other standard storage forms as plug and play options (pandas does this -- i.e. steal pandas conversion options as plugins as they're nice features)
- Maybe lean on some of the other data transport ideas between kernels and components from elsewhere nteract??
- Think a little more about secondary language support (R is nice but we'd want support in many languages for the most common transports)
