# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Interferometric Analysis Configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from perseo_quality.interferometric_analysis.config import InterferometricConfig

from sct.analyses.interferometry.resources import config_schema
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class SCTInterferometricAnalysisConfig(AnalysisConfigABC):
    """SCT Interferometric Analysis configuration"""

    base_config: InterferometricConfig = field(default_factory=InterferometricConfig)
    config_group_name = "interferometric_analysis"
    validation_schema = Path(config_schema)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTInterferometricAnalysisConfig:
        """Convert from dict"""
        return cls(base_config=InterferometricConfig.from_dict(arg=arg))

    def to_dict(self):
        """Convert to dict"""
        out = asdict(self.base_config)

        if not isinstance(self.base_config.coherence_kernel, (tuple, list)):
            out["coherence_kernel"] = (out["coherence_kernel"], out["coherence_kernel"])

        return {self.config_group_name: out}
