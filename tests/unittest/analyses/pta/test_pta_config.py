# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Point Target Analysis Configuration"""

from pathlib import Path

import pytest
from jsonschema.exceptions import ValidationError
from perseo_perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters
from perseo_perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from perseo_quality.core.generic_dataclasses import MaskingMethod
from perseo_quality.point_targets_analysis.config import IRFParameters, PointTargetAnalysisConfig, RCSParameters

from sct.analyses.point_target.config import (
    IonosphericCorrectionsConf,
    SCTPointTargetAnalysisConfig,
    SCTPointTargetAnalysisCorrectionsConf,
    TroposphericCorrectionsConf,
)
from sct.configuration.common import InvalidConfigurationFile

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


def test_full_point_target_analysis_reading(tmp_path) -> None:
    """Test point_target full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(point_target_analysis_toml)

    config = SCTPointTargetAnalysisConfig.from_toml(path_to_file)

    assert isinstance(config, SCTPointTargetAnalysisConfig)
    _validate_pta_config(config)


def test_reading_errors_0(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [point_target_analysis.corrections]
    enable_ionospheric_correction = true

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTPointTargetAnalysisConfig.from_toml(path_to_file)


def test_reading_errors_1(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [point_target_analysis.corrections]
    enable_tropospheric_correction = true

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTPointTargetAnalysisConfig.from_toml(path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(point_target_analysis_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = SCTPointTargetAnalysisConfig.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = SCTPointTargetAnalysisConfig.from_toml(path_to_new_file)

    assert new_config == config


def test_from_dict():
    config = SCTPointTargetAnalysisConfig.from_dict(
        {
            "perform_irf": False,
            "perform_rcs": True,
            "evaluate_pslr": False,
            "evaluate_islr": True,
            "evaluate_sslr": False,
            "evaluate_localization": True,
            "ale_validity_limits": [99, 99],
        }
    )
    assert isinstance(config, SCTPointTargetAnalysisConfig)
    assert config.base_config.perform_irf is False
    assert config.base_config.perform_rcs is True
    assert config.base_config.ale_limits == (99, 99)


def test_from_dict_invalid_key():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        SCTPointTargetAnalysisConfig.from_dict({"invalid_key": True})


def test_to_dict():
    config = SCTPointTargetAnalysisConfig()
    d = config.to_dict()
    assert "point_target_analysis" in d


def test_ionospheric_corrections_conf_from_dict():
    config = IonosphericCorrectionsConf.from_dict({"maps_directory": "test_dir", "analysis_center": "jpl"})
    assert config.maps_directory == Path("test_dir")
    assert config.analysis_center == IonosphericAnalysisCenters.JPL


def test_ionospheric_corrections_conf_from_dict_missing_required():
    with pytest.raises(InvalidConfigurationFile, match="required"):
        IonosphericCorrectionsConf.from_dict({"analysis_center": "jpl"})


def test_ionospheric_corrections_conf_from_dict_unrecognized():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        IonosphericCorrectionsConf.from_dict({"maps_directory": "test", "bad_key": True})


def test_ionospheric_corrections_conf_to_dict():
    config = IonosphericCorrectionsConf(maps_directory=Path("test"), analysis_center=IonosphericAnalysisCenters.JPL)
    d = config.to_dict()
    assert d["maps_directory"] == "test"
    assert d["analysis_center"] == "jpl"


def test_tropospheric_corrections_conf_from_dict():
    config = TroposphericCorrectionsConf.from_dict({"maps_directory": "test_dir", "map_grid_resolution": "fine"})
    assert config.maps_directory == Path("test_dir")
    assert config.map_grid_resolution == TroposphericGRIDResolution.FINE


def test_tropospheric_corrections_conf_from_dict_missing_required():
    with pytest.raises(InvalidConfigurationFile, match="required"):
        TroposphericCorrectionsConf.from_dict({"map_grid_resolution": "fine"})


def test_tropospheric_corrections_conf_from_dict_unrecognized():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        TroposphericCorrectionsConf.from_dict({"maps_directory": "test", "bad_key": True})


def test_tropospheric_corrections_conf_to_dict():
    config = TroposphericCorrectionsConf(
        maps_directory=Path("test"), map_grid_resolution=TroposphericGRIDResolution.FINE
    )
    d = config.to_dict()
    assert d["maps_directory"] == "test"
    assert d["map_grid_resolution"] == "fine"


def test_pta_corrections_conf_from_dict():
    config = SCTPointTargetAnalysisCorrectionsConf.from_dict(
        {
            "enable_solid_tides_correction": False,
            "enable_ionospheric_correction": True,
            "ionosphere": {"maps_directory": "iono_dir", "analysis_center": "jpl"},
            "troposphere": {"maps_directory": "tropo_dir"},
        }
    )
    assert config.enable_solid_tides_correction is False
    assert config.ionosphere.maps_directory == Path("iono_dir")
    assert config.troposphere.maps_directory == Path("tropo_dir")


def test_pta_corrections_conf_from_dict_invalid_key():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        SCTPointTargetAnalysisCorrectionsConf.from_dict({"bad_key": True})


def test_pta_corrections_conf_to_dict():
    config = SCTPointTargetAnalysisCorrectionsConf(
        enable_ionospheric_correction=True,
        ionosphere=IonosphericCorrectionsConf(
            maps_directory=Path("iono"), analysis_center=IonosphericAnalysisCenters.JPL
        ),
    )
    d = config.to_dict()
    assert d["enable_ionospheric_correction"] is True
    assert d["ionosphere"]["maps_directory"] == "iono"
    assert d["ionosphere"]["analysis_center"] == "jpl"


def test_base_config_to_dict():
    config = SCTPointTargetAnalysisConfig()
    d = SCTPointTargetAnalysisConfig.base_config_to_dict(config.base_config)
    assert "advanced_configuration" in d
    assert "irf_parameters" in d["advanced_configuration"]
    assert "rcs_parameters" in d["advanced_configuration"]


def test_base_config_from_dict():
    arg = {
        "perform_irf": True,
        "perform_rcs": False,
        "ale_validity_limits": [50, 50],
        "advanced_configuration": {
            "irf_parameters": {"peak_finding_roi_size": [1, 1], "analysis_roi_size": [2, 2]},
            "rcs_parameters": {"interpolation_factor": 8, "roi_dimension": 128},
        },
    }
    pta_config = SCTPointTargetAnalysisConfig.base_config_from_dict(arg)
    assert pta_config.perform_irf is True
    assert pta_config.perform_rcs is False
    assert pta_config.ale_limits == (50, 50)


def test_empty_config(tmp_path) -> None:
    """Test empty configuration"""
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(general_config_toml)

        SCTPointTargetAnalysisConfig.from_toml(path_to_file)
