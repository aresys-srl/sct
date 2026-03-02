# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing reading/writing/converting SCT configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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


class SCTConfigurationTest(unittest.TestCase):
    """Testing sct_configuration.py functionalities"""

    def test_init_config(self) -> None:
        """Test general configuration initialization"""
        config = GeneralConfiguration()
        self.assertIsInstance(config, GeneralConfiguration)
        _validate_config(config)

    def test_reading(self) -> None:
        """Test full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(general_config_toml)

            config = GeneralConfiguration.from_toml(path_to_file)

        self.assertIsInstance(config, GeneralConfiguration)
        _validate_config(config, path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(general_config_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

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


if __name__ == "__main__":
    unittest.main()
