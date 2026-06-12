# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Elevation Notch Analysis Configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from perseo_quality.elevation_notch_analysis.config import ElevationNotchConfig

from sct.analyses.elevation_notch.resources import config_schema
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class SCTElevationNotchAnalysisConfig(AnalysisConfigABC):
    """SCT Elevation Notch Analysis configuration"""

    base_config: ElevationNotchConfig = field(default_factory=ElevationNotchConfig)
    config_group_name = "elevation_notch_analysis"
    validation_schema = Path(config_schema)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTElevationNotchAnalysisConfig:
        """Convert from dict"""
        return cls(base_config=ElevationNotchConfig.from_dict(arg))

    def to_dict(self):
        """Convert to dict"""
        return {self.config_group_name: asdict(self.base_config)}
