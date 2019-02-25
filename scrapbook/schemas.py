# -*- coding: utf-8 -*-
"""
schemas.py

Provides the json schema for various versions of scrapbook payloads
"""
import re
import os
import json
import glob


def _load_schema(fname):
    with open(fname) as f:
        return json.load(f)


GLUE_PAYLOAD_PREFIX = "application/scrapbook.scrap"
GLUE_PAYLOAD_FMT = GLUE_PAYLOAD_PREFIX + ".{encoder}+json"
RECORD_PAYLOAD_PREFIX = "application/papermill.record"
JSON_FILE_VERSION_REGEX = r".*scrap\.v([0-9]+)\.json"
SCHEMAS = {
    int(re.search(JSON_FILE_VERSION_REGEX, fname).group(1)): _load_schema(fname)
    for fname in glob.glob(
        os.path.join(os.path.dirname(__file__), "schemas/scrap.v*.json")
    )
    if re.match(
        JSON_FILE_VERSION_REGEX, fname
    )  # Since glob can't perfectly match the regex
}
# Update for any new json payloads and schemas/scrap.v*.json
LATEST_SCRAP_VERSION = 1


def scrap_schema(version=LATEST_SCRAP_VERSION):
    try:
        return SCHEMAS[version]
    except KeyError:
        raise ValueError("No schema found for version {}".format(version))
