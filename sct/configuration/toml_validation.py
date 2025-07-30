# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Toml configuration file validation
----------------------------------
"""

import json
from importlib import resources

from jsonschema import validate

import sct.resources as res_folder

configuration_schema = resources.files(res_folder).joinpath("configuration_schema.json")


def toml_schema_validation(toml_content: dict):
    """Validation of input configuration file for SCT tool.

    Parameters
    ----------
    toml_content : dict
        dictionary containing the parsed toml content
    """
    with open(configuration_schema, "r", encoding="utf-8") as schema_file:  # type: ignore
        json_schema = json.load(schema_file)

    validate(toml_content, json_schema)
