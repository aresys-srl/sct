# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis Configuration
----------------------
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from perseo_quality.tar_analysis.config import AmbiguityRatioConfig

from sct.analyses.ambiguity_ratio.resources import config_schema
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class SCTTargetAmbiguityRatioConfig(AnalysisConfigABC):
    """SCT Target Ambiguity Ratio Analysis configuration"""

    base_config: AmbiguityRatioConfig = field(default_factory=AmbiguityRatioConfig)
    config_group_name = "ambiguity_ratio_analysis"
    validation_schema = Path(config_schema)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTTargetAmbiguityRatioConfig:
        """Convert from dict"""
        return cls(base_config=AmbiguityRatioConfig.from_dict(arg))

    def to_dict(self):
        """Convert to dict"""
        return {self.config_group_name: asdict(self.base_config)}
