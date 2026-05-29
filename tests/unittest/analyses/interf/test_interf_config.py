# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Interferometric Analysis Configuration"""

import pytest
from jsonschema.exceptions import ValidationError
from perseo_quality.interferometric_analysis.config import InterferometricConfig

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""

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


def test_full_interferometric_analysis_reading(tmp_path) -> None:
    """Test interferometric_analysis full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(interferometric_analysis_toml)

    config = SCTInterferometricAnalysisConfig.from_toml(path_to_file)

    assert isinstance(config, SCTInterferometricAnalysisConfig)
    _validate_inter_config(config)


def test_reading_errors_0(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [interferometric_analysis]
    azimuth_blocks_number = "test"
    range_blocks_number = 100
    enable_coherence_computation = true
    coherence_kernel = [28, 15]

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTInterferometricAnalysisConfig.from_toml(path_to_file)


def test_reading_errors_1(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [interferometric_analysis]
    azimuth_blocks_number = 10
    range_blocks_number = 100
    enable_coherence_computation = true
    coherence_kernel = 24

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTInterferometricAnalysisConfig.from_toml(path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(interferometric_analysis_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = SCTInterferometricAnalysisConfig.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = SCTInterferometricAnalysisConfig.from_toml(path_to_new_file)

    assert new_config == config


def test_empty_config(tmp_path) -> None:
    """Test empty configuration"""
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(general_config_toml)

        SCTInterferometricAnalysisConfig.from_toml(path_to_file)
