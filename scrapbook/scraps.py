# -*- coding: utf-8 -*-
"""
scraps.py

Provides the Scrap and Scraps abstractions for housing data
"""
import copy
import pandas as pd

from jsonschema import validate as json_validate, ValidationError
from collections import namedtuple, OrderedDict

from .log import logger
from .schemas import scrap_schema, LATEST_SCRAP_VERSION
from .exceptions import ScrapbookDataException

# dataclasses would be nice here...
_scrap_fields = [
    "name",
    "data",
    "reference",
    "encoder",
    "store",
    "stored_format",
    "display",
]
Scrap = namedtuple("Scrap", _scrap_fields)
# Name is required
Scrap.__new__.__defaults__ = (len(_scrap_fields) - 1) * (None,)


def scrap_to_payload(scrap):
    """Translates scrap data to the output format"""
    payload = {
        "name": scrap.name,
        "data": scrap.data,
        "reference": scrap.reference,
        "encoder": scrap.encoder,
        "store": scrap.store,
        "stored_format": scrap.stored_format,
        "version": LATEST_SCRAP_VERSION,
    }
    # Filter empty fields from the payload
    payload = {k: v for k, v in payload.items() if v is not None}
    # Ensure we're conforming to our schema
    try:
        json_validate(payload, scrap_schema(LATEST_SCRAP_VERSION))
    except ValidationError as e:
        raise ScrapbookDataException(
            "Scrap (name={name}) contents do not conform to required type structures: {error}".format(
                name=scrap.name or "None", error=str(e)
            ),
            [e],
        )
    return payload


def payload_to_scrap(payload):
    """Translates data output format to a scrap"""
    if "version" not in payload:
        raise ScrapbookDataException(
            "Scrap payload (name={}) has no version indicator. "
            "This scrap is invalid and cannot be loaded".format(
                payload.get("name", "None")
            )
        )
    if payload["version"] > LATEST_SCRAP_VERSION:
        logger.warning(
            "Scrap being loaded was saved with a later payload version ({version})"
            "than is known by this version of scrapbook ({latest_version}). "
            "Upgrade scrapbook to ensure data is being loaded as intended".format(
                version=payload["version"], latest_version=LATEST_SCRAP_VERSION
            )
        )
    else:
        try:
            json_validate(payload, scrap_schema(payload["version"]))
        except ValidationError as e:
            raise ScrapbookDataException(
                "Scrap payload (name={name}) contents do not conform to required "
                "type structures: {error}".format(
                    name=payload.get("name", "None"), error=str(e)
                ),
                [e],
            )

    # Perform older version cleanup here
    payload = copy.copy(payload)
    if payload["version"] == 1:
        # This was the only option before
        payload["store"] = "notebook"

    return Scrap(
        name=payload.get("name"),
        data=payload.get("data"),
        reference=payload.get("reference"),
        encoder=payload.get("encoder"),
        store=payload.get("store"),
        stored_format=payload.get("stored_format"),
    )


class Scraps(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Scraps, self).__init__(*args, **kwargs)

    @property
    def data_scraps(self):
        return OrderedDict(
            [
                (k, v)
                for k, v in self.items()
                if v.data is not None or v.reference is not None
            ]
        )

    @property
    def data_dict(self):
        return {name: scrap.data for name, scrap in self.data_scraps.items()}

    @property
    def display_scraps(self):
        return OrderedDict([(k, v) for k, v in self.items() if v.display is not None])

    @property
    def display_dict(self):
        return {name: scrap.display for name, scrap in self.display_scraps.items()}

    @property
    def dataframe(self):
        """pandas dataframe: dataframe of cell scraps"""
        return pd.DataFrame(
            [list(scrap) for scrap in self.values()], columns=_scrap_fields
        )
