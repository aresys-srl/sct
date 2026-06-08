# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Target Ambiguity Ratio Analysis Configuration"""

import pytest
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


def test_full_ambiguity_ratio_analysis_reading(tmp_path) -> None:
    """Test ambiguity_ratio_analysis full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(ambiguity_ratio_analysis_toml)

    config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)

    assert isinstance(config, SCTTargetAmbiguityRatioConfig)
    _validate_ambiguity_config(config)


def test_reading_errors_0(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [ambiguity_ratio_analysis]
    interpolation_factor = 16
    cropping_size = [150, 120, 300]

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(ambiguity_ratio_analysis_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = SCTTargetAmbiguityRatioConfig.from_toml(path_to_new_file)

    assert new_config == config


def test_from_dict():
    config = SCTTargetAmbiguityRatioConfig.from_dict({"interpolation_factor": 16, "cropping_size": [150, 120]})
    assert isinstance(config, SCTTargetAmbiguityRatioConfig)
    assert config.base_config.interpolation_factor == 16
    assert config.base_config.cropping_size == (150, 120)


def test_to_dict():
    config = SCTTargetAmbiguityRatioConfig()
    d = config.to_dict()
    assert "ambiguity_ratio_analysis" in d
    assert "interpolation_factor" in d["ambiguity_ratio_analysis"]
    assert "cropping_size" in d["ambiguity_ratio_analysis"]


def test_empty_config(tmp_path) -> None:
    """Test empty configuration"""
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(general_config_toml)

        SCTTargetAmbiguityRatioConfig.from_toml(path_to_file)
