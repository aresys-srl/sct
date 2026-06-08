# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Spectral Analysis Configuration"""

import pytest
from jsonschema.exceptions import ValidationError

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.configuration.common import InvalidConfigurationFile

general_config_toml = """

[general]
save_log = true
save_config_copy = true

"""

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


def test_full_spectral_analysis_reading(tmp_path) -> None:
    """Test spectral_analysis full configuration reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(spectral_analysis_toml)

    config = SCTSpectralAnalysisConfig.from_toml(path_to_file)

    assert isinstance(config, SCTSpectralAnalysisConfig)
    _validate_spectral_config(config)


def test_reading_errors_0(tmp_path) -> None:
    """Test reading with errors"""
    partial_toml = """

    [spectral_analysis]
    cropping_size = [200, 120, 300]

    """
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(partial_toml)

        SCTSpectralAnalysisConfig.from_toml(path_to_file)


def test_dump_read(tmp_path) -> None:
    """Test full configuration dump to toml and reading"""
    path_to_file = tmp_path.joinpath("test.toml")
    path_to_file.write_text(spectral_analysis_toml)
    path_to_new_file = tmp_path.joinpath("dump.toml")

    # reading config
    config = SCTSpectralAnalysisConfig.from_toml(path_to_file)
    # dumping config
    config.to_toml(path_to_new_file)

    # compare config
    new_config = SCTSpectralAnalysisConfig.from_toml(path_to_new_file)

    assert new_config == config


def test_from_dict():
    config = SCTSpectralAnalysisConfig.from_dict({"cropping_size": [200, 120], "azimuth_block_size": 1500})
    assert isinstance(config, SCTSpectralAnalysisConfig)
    assert config.cropping_size == (200, 120)
    assert config.azimuth_block_size == 1500


def test_from_dict_invalid_key():
    with pytest.raises(InvalidConfigurationFile, match="not supported"):
        SCTSpectralAnalysisConfig.from_dict({"invalid_key": True})


def test_to_dict():
    config = SCTSpectralAnalysisConfig()
    d = config.to_dict()
    assert "spectral_analysis" in d


def test_empty_config(tmp_path) -> None:
    """Test empty configuration"""
    with pytest.raises(ValidationError):
        path_to_file = tmp_path.joinpath("test.toml")
        path_to_file.write_text(general_config_toml)

        SCTSpectralAnalysisConfig.from_toml(path_to_file)
