# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Common configuration utilities
------------------------------
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate


class InvalidConfigurationFile(RuntimeError):
    """Invalid SCT .toml configuration file"""


def toml_schema_validation(content: dict, schema_path: str | Path):
    """Validation of input configuration file for SCT tool.

    Parameters
    ----------
    content : dict
        dictionary containing the parsed toml content
    schema_path : str | Path
        path to the json schema file
    """
    assert str(schema_path).endswith(".json")
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        json_schema = json.load(schema_file)

    validate(content, json_schema)
