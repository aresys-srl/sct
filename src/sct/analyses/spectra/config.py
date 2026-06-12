# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Spectral Analysis Configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path

from sct.analyses.spectra.resources import config_schema
from sct.configuration.common import InvalidConfigurationFile
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class SCTSpectralAnalysisConfig(AnalysisConfigABC):
    """SCT Spectral Analysis configuration"""

    cropping_size: tuple[int, int] = (128, 128)
    azimuth_block_size: int = 2000
    config_group_name = "spectral_analysis"
    validation_schema = Path(config_schema)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTSpectralAnalysisConfig:
        """Convert from dict"""
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTSpectralAnalysisConfig: {key} not supported")
            value = tuple(value) if key == "cropping_size" else value
            setattr(out, key, value)

        return out

    def to_dict(self):
        """Convert to dict"""
        return {self.config_group_name: asdict(self)}
