"""Testing configuration/config_abc.py"""

import pytest
import toml

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.configuration.common import InvalidConfigurationFile


def test_from_toml_missing_file():
    with pytest.raises(InvalidConfigurationFile, match="does not exist"):
        SCTSpectralAnalysisConfig.from_toml("nonexistent.toml")


def test_from_toml_wrong_extension(tmp_path):
    wrong_file = tmp_path / "config.txt"
    wrong_file.write_text("")
    with pytest.raises(InvalidConfigurationFile, match="not a .toml"):
        SCTSpectralAnalysisConfig.from_toml(wrong_file)


def test_from_toml_invalid_toml_content(tmp_path):
    invalid_file = tmp_path / "config.toml"
    invalid_file.write_text("not valid toml {{")
    with pytest.raises(toml.TomlDecodeError):
        SCTSpectralAnalysisConfig.from_toml(invalid_file)


def test_to_toml(tmp_path):
    config = SCTSpectralAnalysisConfig()
    out_file = tmp_path / "dump.toml"
    config.to_toml(out_file)
    assert out_file.exists()
    content = toml.load(out_file)
    assert "spectral_analysis" in content
