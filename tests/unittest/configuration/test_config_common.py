"""Testing configuration/common.py"""

import pytest
from jsonschema.exceptions import ValidationError

from sct.configuration.common import toml_schema_validation
from sct.resources import config_schema


def test_toml_schema_validation_valid():
    valid_content = {"general": {"save_log": True, "save_config_copy": True}}
    toml_schema_validation(content=valid_content, schema_path=config_schema)


def test_toml_schema_validation_invalid():
    invalid_content = {"general": {"save_log": "not_a_bool"}}
    with pytest.raises(ValidationError):
        toml_schema_validation(content=invalid_content, schema_path=config_schema)


def test_toml_schema_validation_invalid_schema_path():
    with pytest.raises(AssertionError):
        toml_schema_validation(content={}, schema_path="not_a_json")


def test_toml_schema_validation_missing_schema_file():
    with pytest.raises(FileNotFoundError):
        toml_schema_validation(content={}, schema_path="missing.json")
