# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Target Ambiguity Ratio Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError

from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""

ambiguity_ratio_analysis_toml = """

[ambiguity_ratio_analysis]
interpolation_factor = 16
cropping_size = [150, 120]

"""


def _validate_ambiguity_config(config: SCTTargetAmbiguityRatioConfig) -> None:
    """Validating correct reading of ambiguity ratio analysis configuration from file.

    Parameters
    ----------
    config : SCTTargetAmbiguityRatioConfig
        sct ambiguity ratio analysis configuration
    """

    assert isinstance(config, SCTTargetAmbiguityRatioConfig)

    assert isinstance(config.base_config.interpolation_factor, int)
    assert config.base_config.interpolation_factor == 16
    assert isinstance(config.base_config.cropping_size, tuple)
    assert config.base_config.cropping_size == (150, 120)


class TARConfigurationTest(unittest.TestCase):
    """Test target ambiguity ratio analysis configuration"""

    def test_full_ambiguity_ratio_analysis_reading(self) -> None:
        """Test ambiguity_ratio_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(ambiguity_ratio_analysis_toml)

            config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTTargetAmbiguityRatioConfig)
        _validate_ambiguity_config(config)

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [ambiguity_ratio_analysis]
        interpolation_factor = 16
        cropping_size = [150, 120, 300]

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(ambiguity_ratio_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_new_file)

        assert new_config == config

    def test_empty_config(self) -> None:
        """Test empty configuration"""
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(general_config_toml)

                SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)


if __name__ == "__main__":
    unittest.main()
