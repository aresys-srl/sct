# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Interferometric Analysis Configuration"""

import pytest
from jsonschema.exceptions import ValidationError
from perseo_quality.elevation_notch_analysis.config import ElevationNotchConfig

from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""

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


def test_full_elevation_notch_analysis_reading(tmp_path) -> None:
    """Test elevation_notch_analysis full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(elevation_notch_analysis_toml)

    config = SCTElevationNotchAnalysisConfig.from_toml(path_to_file)

    assert isinstance(config, SCTElevationNotchAnalysisConfig)
    _validate_notch_config(config)


def test_reading_errors_0(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [elevation_notch_analysis]
    azimuth_block_size = "test"

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTElevationNotchAnalysisConfig.from_toml(path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(elevation_notch_analysis_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = SCTElevationNotchAnalysisConfig.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = SCTElevationNotchAnalysisConfig.from_toml(path_to_new_file)

    assert new_config == config


def test_empty_config(tmp_path) -> None:
    """Test empty configuration"""
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(general_config_toml)

        SCTElevationNotchAnalysisConfig.from_toml(path_to_file)
