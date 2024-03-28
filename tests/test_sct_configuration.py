# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing reading/writing/converting SCT configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from arepyextras.perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters
from arepyextras.perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from arepyextras.quality.core.generic_dataclasses import MaskingMethod, SARRadiometricQuantity
from arepyextras.quality.interferometric_analysis.config import InterferometricConfig
from arepyextras.quality.point_targets_analysis.config import IRFParameters, PointTargetAnalysisConfig, RCSParameters
from arepyextras.quality.radiometric_analysis.config import (
    ProfileExtractionParameters,
    Radiometric2DHistogramParameters,
    RadiometricProfilesConfig,
)
from jsonschema.exceptions import ValidationError

from sct.configuration.sct_configuration import (
    SCTConfiguration,
    SCTInterferometricAnalysisConfig,
    SCTPointTargetAnalysisConfig,
    SCTRadiometricAnalysisConfig,
)

point_target_analysis_toml = """

[point_target_analysis]
perform_irf = false
perform_rcs = true
evaluate_pslr = false
evaluate_islr = true
evaluate_sslr = false
evaluate_localization = true
ale_validity_limits = [99, 99]

[point_target_analysis.corrections]
enable_etad_corrections = false
enable_solid_tides_correction = true
enable_plate_tectonics_correction = false
enable_sensor_specific_processing_corrections = true
enable_ionospheric_correction = true
enable_tropospheric_correction = true
etad_product_path = "aaa"

[point_target_analysis.corrections.ionosphere]
ionospheric_maps_directory = "bbb"
ionospheric_analysis_center = "cor"

[point_target_analysis.corrections.troposphere]
tropospheric_maps_directory = "ccc"
tropospheric_map_grid_resolution = "fine"

[point_target_analysis.advanced_configuration.irf_parameters]
peak_finding_roi_size = [1, 1]
analysis_roi_size = [2, 2]
oversampling_factor = 80
zero_doppler_abs_squint_threshold_deg = 2.6
masking_method = "peak"

[point_target_analysis.advanced_configuration.rcs_parameters]
interpolation_factor = 8
roi_dimension = 128
calibration_factor = 1.0
resampling_factor = 7.3

"""


radiometric_analysis_toml = """

[radiometric_analysis]
input_quantity = "sigma_nought"
azimuth_block_size = 23
range_pixel_margin = 800
radiometric_correction_exponent = 250.3

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

interferometric_analysis_toml = """

[interferometric_analysis]
azimuth_blocks_number = 1000
range_blocks_number = 100
enable_coherence_computation = true
coherence_kernel = [28, 15]
coherence_bins_number = 800

"""


def _validate_pta_config(config: SCTPointTargetAnalysisConfig) -> None:
    """Validating correct reading of point target configuration from file.

    Parameters
    ----------
    config : SCTPointTargetAnalysisConfig
        sct point target configuration
    """

    assert isinstance(config, SCTPointTargetAnalysisConfig)
    assert config.enable_etad_corrections is False
    assert config.enable_solid_tides_correction is True
    assert config.enable_plate_tectonics_correction is False
    assert config.enable_sensor_specific_processing_corrections is True
    assert config.enable_ionospheric_correction is True
    assert config.enable_tropospheric_correction is True
    assert config.etad_product_path == Path("aaa")
    assert config.ionospheric_maps_directory == Path("bbb")
    assert config.tropospheric_maps_directory == Path("ccc")
    assert isinstance(config.ionospheric_analysis_center, IonosphericAnalysisCenters)
    assert config.ionospheric_analysis_center == IonosphericAnalysisCenters.COR
    assert isinstance(config.tropospheric_map_grid_resolution, TroposphericGRIDResolution)
    assert config.tropospheric_map_grid_resolution == TroposphericGRIDResolution.FINE

    pta_config = config.base_config
    assert isinstance(pta_config, PointTargetAnalysisConfig)
    assert pta_config.perform_irf is False
    assert pta_config.perform_rcs is True
    assert pta_config.evaluate_pslr is False
    assert pta_config.evaluate_islr is True
    assert pta_config.evaluate_sslr is False
    assert pta_config.evaluate_localization is True
    assert pta_config.ale_limits == (99, 99)

    irf_config = pta_config.irf_parameters
    assert isinstance(irf_config, IRFParameters)
    assert irf_config.peak_finding_roi_size == (1, 1)
    assert irf_config.analysis_roi_size == (2, 2)
    assert irf_config.oversampling_factor == 80
    assert irf_config.peak_finding_roi_size == (1, 1)
    assert irf_config.zero_doppler_abs_squint_threshold_deg == 2.6
    assert isinstance(irf_config.masking_method, MaskingMethod)
    assert irf_config.masking_method == MaskingMethod.PEAK

    rcs_config = pta_config.rcs_parameters
    assert isinstance(rcs_config, RCSParameters)
    assert rcs_config.interpolation_factor == 8
    assert rcs_config.roi_dimension == 128
    assert rcs_config.calibration_factor == 1.0
    assert rcs_config.resampling_factor == 7.3


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
    assert isinstance(ra_config.input_quantity, SARRadiometricQuantity)
    assert ra_config.input_quantity == SARRadiometricQuantity.SIGMA_NOUGHT
    assert ra_config.azimuth_block_size == 23
    assert ra_config.range_pixel_margin == 800
    assert ra_config.radiometric_correction_exponent == 250.3

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


class SCTConfigurationTest(unittest.TestCase):
    """Testing sct_configuration.py functionalities"""

    def setUp(self) -> None:
        self.full_toml = point_target_analysis_toml + radiometric_analysis_toml + interferometric_analysis_toml

    def test_full_point_target_analysis_reading(self) -> None:
        """Test point_target full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(point_target_analysis_toml)

            config = SCTConfiguration.from_toml(path_to_file)

        self.assertIsInstance(config, SCTConfiguration)
        _validate_pta_config(config.point_target_analysis)

    def test_full_radiometric_analysis_reading(self) -> None:
        """Test radiometric_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(radiometric_analysis_toml)

            config = SCTConfiguration.from_toml(path_to_file)

        self.assertIsInstance(config, SCTConfiguration)
        _validate_ra_config(config.radiometric_analysis)

    def test_full_interferometric_analysis_reading(self) -> None:
        """Test interferometric_analysis full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(interferometric_analysis_toml)

            config = SCTConfiguration.from_toml(path_to_file)

        self.assertIsInstance(config, SCTConfiguration)
        _validate_inter_config(config.interferometric_analysis)

    def test_full_config_reading(self) -> None:
        """Test full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(self.full_toml)

            config = SCTConfiguration.from_toml(path_to_file)

        self.assertIsInstance(config, SCTConfiguration)
        _validate_pta_config(config.point_target_analysis)
        _validate_ra_config(config.radiometric_analysis)
        _validate_inter_config(config.interferometric_analysis)

    def test_partial_config_reading(self) -> None:
        """Test full configuration reading"""
        partial_toml = """
        
        [point_target_analysis]
        perform_irf = false
        evaluate_islr = true

        [point_target_analysis.advanced_configuration.irf_parameters]
        analysis_roi_size = [2, 2]

        [radiometric_analysis.advanced_configuration.profile_extraction_parameters]
        filtering_kernel_size = [ 18, 18,]
        outliers_percentile_boundaries = [ 5, 95,]

        [interferometric_analysis]
        range_blocks_number = 100
        coherence_kernel = [35, 2]

        """
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(partial_toml)

            config = SCTConfiguration.from_toml(path_to_file)

            self.assertIsInstance(config, SCTConfiguration)

        self.assertIsInstance(config.point_target_analysis, SCTPointTargetAnalysisConfig)
        self.assertFalse(config.point_target_analysis.base_config.perform_irf)
        self.assertTrue(config.point_target_analysis.base_config.evaluate_islr)
        self.assertEqual(config.point_target_analysis.base_config.irf_parameters.analysis_roi_size, (2, 2))
        self.assertIsInstance(config.radiometric_analysis, SCTRadiometricAnalysisConfig)
        self.assertEqual(
            config.radiometric_analysis.base_config.profile_extraction_parameters.filtering_kernel_size, (18, 18)
        )
        self.assertEqual(
            config.radiometric_analysis.base_config.profile_extraction_parameters.outliers_percentile_boundaries,
            (5, 95),
        )
        self.assertIsInstance(config.interferometric_analysis, SCTInterferometricAnalysisConfig)
        self.assertEqual(config.interferometric_analysis.base_config.coherence_kernel, (35, 2))
        self.assertEqual(config.interferometric_analysis.base_config.range_blocks_number, 100)
        self.assertIsNone(config.interferometric_analysis.base_config.azimuth_blocks_number, None)

    def test_dump_read_default(self) -> None:
        """Test full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            default_config = SCTConfiguration()
            default_config.dump_to_toml(path_to_file)
            default_config_read = SCTConfiguration.from_toml(path_to_file)

        self.assertEqual(default_config.general, default_config_read.general)
        self.assertEqual(default_config.point_target_analysis, default_config_read.point_target_analysis)
        self.assertEqual(default_config.radiometric_analysis, default_config_read.radiometric_analysis)
        default_config.interferometric_analysis.base_config.coherence_kernel = (
            default_config.interferometric_analysis.base_config.coherence_kernel,
            default_config.interferometric_analysis.base_config.coherence_kernel,
        )
        self.assertEqual(default_config.interferometric_analysis, default_config_read.interferometric_analysis)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(self.full_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTConfiguration.from_toml(path_to_file)
            # dumping config
            config.dump_to_toml(path_to_new_file)

            # compare config
            new_config = SCTConfiguration.from_toml(path_to_new_file)

        assert new_config.general == config.general
        assert new_config.point_target_analysis == config.point_target_analysis
        assert new_config.radiometric_analysis == config.radiometric_analysis
        assert new_config.interferometric_analysis == config.interferometric_analysis

    def test_reading_errors_0(self) -> None:
        """Test reading with errors"""
        partial_toml = """
        
        [point_target_analysis.corrections]
        enable_ionospheric_correction = true

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTConfiguration.from_toml(path_to_file)

    def test_reading_errors_1(self) -> None:
        """Test reading with errors"""
        partial_toml = """
        
        [point_target_analysis.corrections]
        enable_tropospheric_correction = true

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTConfiguration.from_toml(path_to_file)

    def test_reading_errors_2(self) -> None:
        """Test reading with errors"""
        partial_toml = """
        
        [radiometric_analysis]
        input_quantity = "nought"

        """
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(partial_toml)

                SCTConfiguration.from_toml(path_to_file)


if __name__ == "__main__":
    unittest.main()
