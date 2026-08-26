# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing configuration/config_abc.py"""

from dataclasses import dataclass
from pathlib import Path

import pytest
import toml

from sct.configuration.common import InvalidConfigurationFile
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class _TestAnalysisConfig(AnalysisConfigABC):
    config_group_name = "test_analysis"
    validation_schema = Path("/nonexistent")

    @classmethod
    def from_dict(cls, arg):
        return cls()

    def to_dict(self):
        return {self.config_group_name: {}}


def test_from_toml_missing_file():
    with pytest.raises(InvalidConfigurationFile, match="does not exist"):
        _TestAnalysisConfig.from_toml("nonexistent.toml")


def test_from_toml_wrong_extension(tmp_path):
    wrong_file = tmp_path / "config.txt"
    wrong_file.write_text("")
    with pytest.raises(InvalidConfigurationFile, match="not a .toml"):
        _TestAnalysisConfig.from_toml(wrong_file)


def test_from_toml_invalid_toml_content(tmp_path):
    invalid_file = tmp_path / "config.toml"
    invalid_file.write_text("not valid toml {{")
    with pytest.raises(toml.TomlDecodeError):
        _TestAnalysisConfig.from_toml(invalid_file)


def test_to_toml(tmp_path):
    config = _TestAnalysisConfig()
    out_file = tmp_path / "dump.toml"
    config.to_toml(out_file)
    assert out_file.exists()
    content = toml.load(out_file)
    assert "test_analysis" in content
