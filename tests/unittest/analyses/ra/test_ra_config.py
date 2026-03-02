# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Radiometric Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError
from perseo_quality.radiometric_analysis.block_wise.config import (
    ProfileExtractionParameters,
    Radiometric2DHistogramParameters,
    RadiometricProfilesConfig,
)

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig

radiometric_analysis_toml = """

[radiometric_analysis]
azimuth_block_size = 23
range_pixel_margin = 800

[radiometric_analysis.advanced_configuration.profile_extraction_parameters]
outlier_removal = false
smoothening_filter = true
filtering_kernel_size = [ 18, 18,]
outliers_percentile_boundaries = [ 5, 95,]
outliers_kernel_size = [ 1, 1,]

[radiometric_analysis.advanced_configuration.histogram_parameters]
x_bins_step = 10
y_bins_num = 101
y_bins_center_margin = 3

"""


def _validate_ra_config(config: SCTRadiometricAnalysisConfig) -> None:
    """Validating correct reading of radiometric configuration from file.

    Parameters
    ----------
    config : SCTRadiometricAnalysisConfig
        sct radiometric configuration
    """

    assert isinstance(config, SCTRadiometricAnalysisConfig)

    ra_config = config.base_config
    assert isinstance(ra_config, RadiometricProfilesConfig)
    assert ra_config.azimuth_block_size == 23
    assert ra_config.range_pixel_margin == 800

    hist_config = ra_config.histogram_parameters
    assert isinstance(hist_config, Radiometric2DHistogramParameters)
    assert hist_config.x_bins_step == 10
    assert hist_config.y_bins_num == 101
    assert hist_config.y_bins_center_margin == 3

    profile_config = ra_config.profile_extraction_parameters
    assert isinstance(profile_config, ProfileExtractionParameters)
    assert profile_config.outlier_removal is False
    assert profile_config.smoothening_filter is True
    assert profile_config.filtering_kernel_size == (18, 18)
    assert profile_config.outliers_percentile_boundaries == (5, 95)
    assert profile_config.outliers_kernel_size == (1, 1)


class RAConfigurationTest(unittest.TestCase):
    """Test radiometric analysis configuration"""

    def test_full_radiometric_analysis_reading(self) -> None:
        """Test radiometric_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(radiometric_analysis_toml)

            config = SCTRadiometricAnalysisConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTRadiometricAnalysisConfig)
        _validate_ra_config(config)

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [radiometric_analysis]
        azimuth_block_size = "test"
        range_pixel_margin = 800

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTRadiometricAnalysisConfig.from_toml(path_to_file)

    def test_reading_errors_1(self) -> None:
        """Test reading with errors"""
        partial_toml = """

        [radiometric_analysis.advanced_configuration.histogram_parameters]
        x_bins_step = 10
        y_bins_num = [10, 10]
        y_bins_center_margin = 3

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTRadiometricAnalysisConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(radiometric_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTRadiometricAnalysisConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTRadiometricAnalysisConfig.from_toml(path_to_new_file)

        assert new_config == config


if __name__ == "__main__":
    unittest.main()
