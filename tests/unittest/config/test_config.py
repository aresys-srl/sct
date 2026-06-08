# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing reading/writing/converting SCT configuration"""

from pathlib import Path

import pytest

from sct.configuration.common import InvalidConfigurationFile
from sct.configuration.config import GeneralConfiguration

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""


def _validate_config(config: GeneralConfiguration, path: Path | None = None) -> None:
    """Validating correct reading of configuration from file.

    Parameters
    ----------
    config : GeneralConfiguration
        sct general configuration
    path : Path | None
        path to the configuration file
    """

    assert isinstance(config, GeneralConfiguration)

    assert isinstance(config.save_log, bool)
    assert isinstance(config.save_config_copy, bool)
    if path is None:
        assert config.toml_path is None
    else:
        assert isinstance(config.toml_path, Path)
        assert config.toml_path == path


def test_init_config() -> None:
    """Test general configuration initialization"""
    config = GeneralConfiguration()
    assert isinstance(config, GeneralConfiguration)
    _validate_config(config)


def test_reading(tmp_path) -> None:
    """Test full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(general_config_toml)

    config = GeneralConfiguration.from_toml(path_to_file)

    assert isinstance(config, GeneralConfiguration)
    _validate_config(config, path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(general_config_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = GeneralConfiguration.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = GeneralConfiguration.from_toml(path_to_new_file)

    assert new_config.save_config_copy == config.save_config_copy
    assert new_config.save_log == config.save_log
    assert new_config.toml_path == path_to_new_file
    assert config.toml_path == path_to_file


def test_from_dict():
    config = GeneralConfiguration.from_dict({"save_log": False, "save_config_copy": True})
    assert isinstance(config, GeneralConfiguration)
    assert config.save_log is False
    assert config.save_config_copy is True


def test_from_dict_invalid_key():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        GeneralConfiguration.from_dict({"nonexistent_key": True})


def test_to_dict():
    config = GeneralConfiguration(save_log=True, save_config_copy=False)
    d = config.to_dict()
    assert d == {"save_log": True, "save_config_copy": False, "toml_path": None}


def test_from_toml_missing_general_section(tmp_path):
    toml_content = """
    [other_section]
    key = "value"
    """
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(toml_content)
    config = GeneralConfiguration.from_toml(path_to_file)
    assert config.save_log is True
    assert config.save_config_copy is True


def test_from_toml_missing_file():
    with pytest.raises(InvalidConfigurationFile, match="does not exist"):
        GeneralConfiguration.from_toml("nonexistent.toml")


def test_from_toml_wrong_extension(tmp_path):
    wrong_file = tmp_path / "config.txt"
    wrong_file.write_text("")
    with pytest.raises(InvalidConfigurationFile, match="not a .toml"):
        GeneralConfiguration.from_toml(wrong_file)
