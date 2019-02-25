# -*- coding: utf-8 -*-


class ScrapbookException(ValueError):
    """Raised when an exception is encountered when operating on a notebook."""


class ScrapbookMissingEncoder(ScrapbookException):
    """Raised when no encoder is found to tranforming data"""


class ScrapbookDataException(ScrapbookException):
    """Raised when a data translation exception is encountered"""

    def __init__(self, message, data_errors=None):
        super(ScrapbookDataException, self).__init__(message)
        self.data_errors = data_errors
