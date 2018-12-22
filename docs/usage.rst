Usage
=====

*Under active design and development. Functionality may change.*

Ideas and possible approaches for development
---------------------------------------------

- Consider Apache Arrow for dataframe-like saves
- Continue accepting JSON save format (backwards compatibility)
- Support some other binary forms (plug and play options?)
- Support other standard storage forms as plug and play options, like pandas
  does (Use pandas conversion metaphors as plugins as pandas' implementation is
  a nice feature.)
- Review viability of some of the other data transport ideas between kernels and
  components from elsewhere. nteract??
- Think a little more about secondary language support (R is nice, but we'd want
  support in many languages for the most common transports.)
