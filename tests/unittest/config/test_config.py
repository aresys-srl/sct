# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing reading/writing/converting SCT configuration"""

from pathlib import Path

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
