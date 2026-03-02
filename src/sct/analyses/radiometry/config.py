# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis Configuration
----------------------
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from perseo_quality.radiometric_analysis.block_wise.config import RadiometricProfilesConfig

from sct.analyses.radiometry.resources import config_schema
from sct.configuration.config_abc import AnalysisConfigABC


@dataclass
class SCTRadiometricAnalysisConfig(AnalysisConfigABC):
    """SCT Radiometric Analysis configuration"""

    base_config: RadiometricProfilesConfig = field(default_factory=RadiometricProfilesConfig)
    config_group_name = "radiometric_analysis"
    validation_schema = Path(config_schema)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTRadiometricAnalysisConfig:
        """Convert from dict"""
        arg.update(arg.pop("advanced_configuration", {}))
        return cls(base_config=RadiometricProfilesConfig.from_dict(arg))

    def to_dict(self) -> dict:
        """Convert to dict"""

        ra_dict = asdict(self.base_config)
        ra_dict["advanced_configuration"] = {
            "histogram_parameters": ra_dict.pop("histogram_parameters"),
            "profile_extraction_parameters": ra_dict.pop("profile_extraction_parameters"),
        }

        return {self.config_group_name: ra_dict}
