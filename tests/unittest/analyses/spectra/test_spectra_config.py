# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Spectral Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig

spectral_analysis_toml = """

[spectral_analysis]
cropping_size = [200, 120]
azimuth_block_size = 1500

"""


def _validate_spectral_config(config: SCTSpectralAnalysisConfig) -> None:
    """Validating correct reading of spectral analysis configuration from file.

    Parameters
    ----------
    config : SCTSpectralAnalysisConfig
        sct spectral analysis configuration
    """

    assert isinstance(config, SCTSpectralAnalysisConfig)

    assert isinstance(config.cropping_size, tuple)
    assert config.cropping_size == (200, 120)
    assert config.azimuth_block_size == 1500


class SPECTRAConfigurationTest(unittest.TestCase):
    """Test spectral analysis configuration"""

    def test_full_spectral_analysis_reading(self) -> None:
        """Test spectral_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(spectral_analysis_toml)

            config = SCTSpectralAnalysisConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTSpectralAnalysisConfig)
        _validate_spectral_config(config)

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [spectral_analysis]
        cropping_size = [200, 120, 300]

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTSpectralAnalysisConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(spectral_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTSpectralAnalysisConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTSpectralAnalysisConfig.from_toml(path_to_new_file)

        assert new_config == config


if __name__ == "__main__":
    unittest.main()
