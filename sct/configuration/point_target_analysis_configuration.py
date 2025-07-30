# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point target analysis configuration
-----------------------------------
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from arepyextras.perturbations.atmospheric.ionosphere import (
    IonosphericAnalysisCenters,
    TECMappingFunctionIncidenceAngleMethod,
)
from arepyextras.perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from arepyextras.quality.point_targets_analysis.config import PointTargetAnalysisConfig

from sct.configuration.common import InvalidConfigurationFile


@dataclass
class IonosphericCorrectionsConf:
    """SCT Point Target Analysis ionospheric corrections configuration"""

    maps_directory: Path
    analysis_center: IonosphericAnalysisCenters
    tec_incidence_angle_method: TECMappingFunctionIncidenceAngleMethod = (
        TECMappingFunctionIncidenceAngleMethod.GROUND_CONVERTED
    )

    @classmethod
    def from_dict(cls, arg: dict) -> IonosphericCorrectionsConf:
        """Convert from dict"""
        valid_fields = set(f.name for f in fields(cls))
        required_fields = set(("maps_directory",))

        unrecognized_keys = set(arg.keys()) - valid_fields
        missing_keys = required_fields - set(arg.keys())

        if unrecognized_keys:
            raise InvalidConfigurationFile(f"IonosphericCorrectionsConf: {unrecognized_keys} not supported")
        if missing_keys:
            raise InvalidConfigurationFile(f"IonosphericCorrectionsConf: {missing_keys} are required")

        out = cls(
            maps_directory=Path(arg["maps_directory"]),
            analysis_center=IonosphericAnalysisCenters[arg["analysis_center"].upper()],
        )

        for key, value in arg.items():
            if key == "tec_incidence_angle_method":
                out.tec_incidence_angle_method = TECMappingFunctionIncidenceAngleMethod[value.upper()]

        return out

    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            "maps_directory": str(self.maps_directory),
            "analysis_center": self.analysis_center.name.lower(),
            "tec_incidence_angle_method": self.tec_incidence_angle_method.name.lower(),
        }


@dataclass
class TroposphericCorrectionsConf:
    """SCT Point Target Analysis tropospheric corrections configuration"""

    maps_directory: Path
    map_grid_resolution: TroposphericGRIDResolution = TroposphericGRIDResolution.FINE

    @classmethod
    def from_dict(cls, arg: dict) -> TroposphericCorrectionsConf:
        """Convert from dict"""
        required_fields = set(("maps_directory",))
        valid_fields = set(f.name for f in fields(cls))

        unrecognized_keys = set(arg.keys()) - valid_fields
        missing_keys = required_fields - set(arg.keys())

        if unrecognized_keys:
            raise InvalidConfigurationFile(f"TroposphericCorrectionsConf: {unrecognized_keys} not supported")
        if missing_keys:
            raise InvalidConfigurationFile(f"TroposphericCorrectionsConf: {missing_keys} are required")

        out = cls(maps_directory=Path(arg["maps_directory"]))
        if "map_grid_resolution" in arg:
            out.map_grid_resolution = TroposphericGRIDResolution[arg["map_grid_resolution"].upper()]

        return out

    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            "maps_directory": str(self.maps_directory),
            "map_grid_resolution": self.map_grid_resolution.name.lower(),
        }


@dataclass
class SCTPointTargetAnalysisCorrectionsConf:
    """SCT Point Target Analysis corrections configuration"""

    enable_etad_corrections: bool = False
    enable_solid_tides_correction: bool = True
    enable_plate_tectonics_correction: bool = True
    enable_sensor_specific_processing_corrections: bool = True
    enable_ionospheric_correction: bool = False
    enable_tropospheric_correction: bool = False
    ionosphere: IonosphericCorrectionsConf | None = None
    troposphere: TroposphericCorrectionsConf | None = None
    etad_product_path: Path | None = None

    @classmethod
    def from_dict(cls, arg: dict) -> SCTPointTargetAnalysisCorrectionsConf:
        """Convert from dict"""
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTPointTargetAnalysisCorrectionsConfig: {key} not supported")

            if key == "ionosphere":
                out.ionosphere = IonosphericCorrectionsConf.from_dict(value)
            elif key == "troposphere":
                out.troposphere = TroposphericCorrectionsConf.from_dict(value)
            elif key == "etad_product_path" and value is not None:
                setattr(out, key, Path(value))
            else:
                setattr(out, key, value)

        return out

    def to_dict(self) -> dict:
        """Convert to dict"""
        out = asdict(self)

        if self.ionosphere is not None:
            out["ionosphere"] = self.ionosphere.to_dict()
        if self.troposphere is not None:
            out["troposphere"] = self.troposphere.to_dict()

        if self.etad_product_path is not None:
            out["etad_product_path"] = str(self.etad_product_path)
        else:
            out.pop("etad_product_path", None)

        return out


@dataclass
class SCTPointTargetAnalysisConfig:
    """SCT Point Target Analysis configuration"""

    base_config: PointTargetAnalysisConfig = field(default_factory=PointTargetAnalysisConfig)
    corrections: SCTPointTargetAnalysisCorrectionsConf = field(default_factory=SCTPointTargetAnalysisCorrectionsConf)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTPointTargetAnalysisConfig:
        """Convert from dict"""
        out = cls()
        valid_fields: set[str] = set(("corrections", "ale_validity_limits", "advanced_configuration"))
        valid_fields.update(f.name for f in fields(PointTargetAnalysisConfig))

        for key in arg:
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTPointTargetAnalysisConfig: {key} not supported")

        out.corrections = SCTPointTargetAnalysisCorrectionsConf.from_dict(arg.pop("corrections", {}))
        out.base_config = SCTPointTargetAnalysisConfig.base_config_from_dict(arg)

        return out

    def to_dict(self) -> dict:
        """Convert to dict"""
        out = self.base_config_to_dict(self.base_config)
        out["corrections"] = self.corrections.to_dict()

        return out

    @staticmethod
    def base_config_to_dict(base_config: PointTargetAnalysisConfig) -> dict:
        """Convert base config to dict with SCT configuration conventions."""
        config = asdict(base_config)

        pta_ale = config.pop("ale_limits")
        pta_irf = config.pop("irf_parameters")
        if pta_irf["masking_method"] is not None:
            pta_irf["masking_method"] = pta_irf["masking_method"].name.lower()
        pta_rcs = config.pop("rcs_parameters")
        config: dict[str, Any] = dict(
            (k, config[k])
            for k in (
                "perform_irf",
                "perform_rcs",
                "evaluate_pslr",
                "evaluate_islr",
                "evaluate_sslr",
                "evaluate_localization",
            )
        )
        config["ale_validity_limits"] = pta_ale
        config["advanced_configuration"] = {}
        config["advanced_configuration"]["irf_parameters"] = pta_irf
        config["advanced_configuration"]["rcs_parameters"] = pta_rcs

        return config

    @staticmethod
    def base_config_from_dict(arg: dict) -> PointTargetAnalysisConfig:
        """Convert base config from dict with SCT configuration conventions."""
        out = {}
        out.update(arg)
        if "ale_validity_limits" in out:
            out["ale_limits"] = out.pop("ale_validity_limits")

        out.update(out.pop("advanced_configuration", {}))

        return PointTargetAnalysisConfig.from_dict(out)
