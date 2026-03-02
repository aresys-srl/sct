# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Interferometric Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError
from perseo_quality.interferometric_analysis.config import InterferometricConfig

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig

interferometric_analysis_toml = """

[interferometric_analysis]
azimuth_blocks_number = 1000
range_blocks_number = 100
enable_coherence_computation = true
coherence_kernel = [28, 15]
coherence_bins_number = 800

"""


def _validate_inter_config(config: SCTInterferometricAnalysisConfig) -> None:
    """Validating correct reading of interferometric configuration from file.

    Parameters
    ----------
    config : SCTInterferometricAnalysisConfig
        sct interferometric configuration
    """

    assert isinstance(config, SCTInterferometricAnalysisConfig)

    inter_config = config.base_config
    assert isinstance(inter_config, InterferometricConfig)
    assert inter_config.azimuth_blocks_number == 1000
    assert inter_config.range_blocks_number == 100
    assert inter_config.enable_coherence_computation is True
    assert inter_config.coherence_kernel == (28, 15)
    assert inter_config.coherence_bins_number == 800


class INTERFConfigurationTest(unittest.TestCase):
    """Test interferometric analysis configuration"""

    def test_full_interferometric_analysis_reading(self) -> None:
        """Test interferometric_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(interferometric_analysis_toml)

            config = SCTInterferometricAnalysisConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTInterferometricAnalysisConfig)
        _validate_inter_config(config)

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [interferometric_analysis]
        azimuth_blocks_number = "test"
        range_blocks_number = 100
        enable_coherence_computation = true
        coherence_kernel = [28, 15]

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTInterferometricAnalysisConfig.from_toml(path_to_file)

    def test_reading_errors_1(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [interferometric_analysis]
        azimuth_blocks_number = 10
        range_blocks_number = 100
        enable_coherence_computation = true
        coherence_kernel = 24

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTInterferometricAnalysisConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(interferometric_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTInterferometricAnalysisConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTInterferometricAnalysisConfig.from_toml(path_to_new_file)

        assert new_config == config


if __name__ == "__main__":
    unittest.main()
