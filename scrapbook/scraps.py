# -*- coding: utf-8 -*-
"""
scraps.py

Provides the Scrap and Scraps abstractions for housing data
"""
import pandas as pd

from jsonschema import validate as json_validate, ValidationError
from collections import namedtuple, OrderedDict

from .log import logger
from .schemas import scrap_schema, LATEST_SCRAP_VERSION
from .exceptions import ScrapbookDataException

# dataclasses would be nice here...
Scrap = namedtuple("Scrap", ["name", "data", "encoder", "display"])
Scrap.__new__.__defaults__ = (None,)


def scrap_to_payload(scrap):
    """Translates scrap data to the output format"""
    # Apply new keys here as needed (like `ref`)
    payload = {
        "name": scrap.name,
        "data": scrap.data,
        "encoder": scrap.encoder,
        "version": LATEST_SCRAP_VERSION,
    }
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
    # If future schema versions would require further manipulation
    # then implement various version loaders here
    return Scrap(
        name=payload.get("name"),
        data=payload.get("data"),
        encoder=payload.get("encoder"),
    )


class Scraps(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(Scraps, self).__init__(*args, **kwargs)

    @property
    def data_scraps(self):
        return OrderedDict([(k, v) for k, v in self.items() if v.data is not None])

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
            [
                [scrap.name, scrap.data, scrap.encoder, scrap.display]
                for scrap in self.values()
            ],
            columns=["name", "data", "encoder", "display"],
        )
