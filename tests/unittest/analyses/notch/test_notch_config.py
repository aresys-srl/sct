# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Interferometric Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError
from perseo_quality.elevation_notch_analysis.config import ElevationNotchConfig

from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig

elevation_notch_analysis_toml = """

[elevation_notch_analysis]
azimuth_block_size = 2500
range_pixel_margin = 100

"""


def _validate_notch_config(config: SCTElevationNotchAnalysisConfig) -> None:
    """Validating correct reading of elevation notch analysis configuration from file.

    Parameters
    ----------
    config : SCTElevationNotchAnalysisConfig
        sct elevation notch analysis configuration
    """

    assert isinstance(config, SCTElevationNotchAnalysisConfig)

    assert isinstance(config.base_config, ElevationNotchConfig)
    assert isinstance(config.base_config.azimuth_block_size, int)
    assert config.base_config.azimuth_block_size == 2500
    assert isinstance(config.base_config.range_pixel_margin, int)
    assert config.base_config.range_pixel_margin == 100


class NOTCHConfigurationTest(unittest.TestCase):
    """Test elevation notch analysis configuration"""

    def test_full_elevation_notch_analysis_reading(self) -> None:
        """Test elevation_notch_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(elevation_notch_analysis_toml)

            config = SCTElevationNotchAnalysisConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTElevationNotchAnalysisConfig)
        _validate_notch_config(config)

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [elevation_notch_analysis]
        azimuth_block_size = "test"

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTElevationNotchAnalysisConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(elevation_notch_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTElevationNotchAnalysisConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTElevationNotchAnalysisConfig.from_toml(path_to_new_file)

        assert new_config == config


if __name__ == "__main__":
    unittest.main()
