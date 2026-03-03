# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Point Target Analysis Configuration"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema.exceptions import ValidationError
from perseo_perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters
from perseo_perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from perseo_quality.core.generic_dataclasses import MaskingMethod
from perseo_quality.point_targets_analysis.config import IRFParameters, PointTargetAnalysisConfig, RCSParameters

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""


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
enable_solid_tides_correction = true
enable_plate_tectonics_correction = false
enable_sensor_specific_processing_corrections = true
enable_ionospheric_correction = true
enable_tropospheric_correction = true

[point_target_analysis.corrections.ionosphere]
maps_directory = "bbb"
analysis_center = "cor"

[point_target_analysis.corrections.troposphere]
maps_directory = "ccc"
map_grid_resolution = "fine"

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


def _validate_pta_config(config: SCTPointTargetAnalysisConfig) -> None:
    """Validating correct reading of point target configuration from file.

    Parameters
    ----------
    config : SCTPointTargetAnalysisConfig
        sct point target configuration
    """

    assert isinstance(config, SCTPointTargetAnalysisConfig)
    assert config.corrections.enable_solid_tides_correction is True
    assert config.corrections.enable_plate_tectonics_correction is False
    assert config.corrections.enable_sensor_specific_processing_corrections is True
    assert config.corrections.enable_ionospheric_correction is True
    assert config.corrections.enable_tropospheric_correction is True
    assert config.corrections.ionosphere.maps_directory == Path("bbb")
    assert isinstance(config.corrections.ionosphere.analysis_center, IonosphericAnalysisCenters)
    assert config.corrections.ionosphere.analysis_center == IonosphericAnalysisCenters.COR
    assert config.corrections.troposphere.maps_directory == Path("ccc")
    assert isinstance(config.corrections.troposphere.map_grid_resolution, TroposphericGRIDResolution)
    assert config.corrections.troposphere.map_grid_resolution == TroposphericGRIDResolution.FINE

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


class PTAConfigurationTest(unittest.TestCase):
    """Test point target analysis configuration"""

    def test_full_point_target_analysis_reading(self) -> None:
        """Test point_target full configuration reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(point_target_analysis_toml)

            config = SCTPointTargetAnalysisConfig.from_toml(path_to_file)

        self.assertIsInstance(config, SCTPointTargetAnalysisConfig)
        _validate_pta_config(config)

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

                SCTPointTargetAnalysisConfig.from_toml(path_to_file)

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

                SCTPointTargetAnalysisConfig.from_toml(path_to_file)

    def test_dump_read(self) -> None:
        """Test full configuration dump to toml and reading"""
        with TemporaryDirectory() as temp_dir:
            path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
            path_to_file.write_text(point_target_analysis_toml)
            path_to_new_file = Path(temp_dir).joinpath("dump").with_suffix(".toml")

            # reading config
            config = SCTPointTargetAnalysisConfig.from_toml(path_to_file)
            # dumping config
            config.to_toml(path_to_new_file)

            # compare config
            new_config = SCTPointTargetAnalysisConfig.from_toml(path_to_new_file)

        assert new_config == config

    def test_empty_config(self) -> None:
        """Test empty configuration"""
        with self.assertRaises(ValidationError):
            with TemporaryDirectory() as temp_dir:
                path_to_file = Path(temp_dir).joinpath("test").with_suffix(".toml")
                path_to_file.write_text(general_config_toml)

                SCTPointTargetAnalysisConfig.from_toml(path_to_file)


if __name__ == "__main__":
    unittest.main()
