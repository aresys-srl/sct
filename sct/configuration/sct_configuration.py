# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Tool and analyses configuration options
---------------------------------------
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field, fields
from enum import Enum, auto
from pathlib import Path
from typing import Union

import appdirs
import toml
from arepyextras.perturbations.atmospheric.ionosphere import (
    IonosphericAnalysisCenters,
    TECMappingFunctionIncidenceAngleMethod,
)
from arepyextras.perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from arepyextras.quality.interferometric_analysis.config import InterferometricConfig
from arepyextras.quality.point_targets_analysis.config import PointTargetAnalysisConfig
from arepyextras.quality.radiometric_analysis.config import RadiometricProfilesConfig
from jsonschema import validate

from sct import config_schema

USER_SCT_CONFIG_FILE = Path(appdirs.user_config_dir(), "SCT_TOOL", "sct_tool_default_config.toml")
ENVIRONMENT_VARIABLE = "SCT_CONFIG_FILE"

# syncing with logger
log = logging.getLogger("quality_analysis")


class InvalidConfigurationFile(RuntimeError):
    """Invalid SCT .toml configuration file"""


class ConfigSupportedAnalyses(Enum):
    """Configuration supported analyses"""

    INTERFEROMETRY = auto()
    RADIOMETRY = auto()
    POINT_TARGET = auto()


def toml_schema_validation(toml_content: dict):
    """Validation of input configuration file for SCT tool.

    Parameters
    ----------
    toml_content : dict
        dictionary containing the parsed toml content
    """

    with open(config_schema, "r", encoding="utf-8") as f:
        json_schema = json.load(f)

    validate(toml_content, json_schema)


@dataclass
class DefaultConfiguration:
    """SCT Default configuration"""

    save_log: bool = True
    save_config_copy: bool = True

    @classmethod
    def from_dict(cls, arg: dict) -> DefaultConfiguration:
        """Creating a DefaultConfiguration from a dict representing this dataclass.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        DefaultConfiguration
            DefaultConfiguration dataclass initialized from input dictionary
        """
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"DefaultConfiguration: {key} not supported")

            setattr(out, key, value)

        return out


@dataclass
class SCTPointTargetAnalysisConfig:
    """SCT Point Target Analysis configuration"""

    base_config: PointTargetAnalysisConfig = field(default_factory=PointTargetAnalysisConfig)
    enable_etad_corrections: bool = False
    enable_solid_tides_correction: bool = True
    enable_plate_tectonics_correction: bool = True
    enable_sensor_specific_processing_corrections: bool = True
    enable_ionospheric_correction: bool = False
    enable_tropospheric_correction: bool = False
    ionospheric_maps_directory: Path | None = None
    ionospheric_analysis_center: IonosphericAnalysisCenters | None = None
    ionospheric_tec_inc_angle_method: TECMappingFunctionIncidenceAngleMethod = (
        TECMappingFunctionIncidenceAngleMethod.GROUND_CONVERTED
    )
    tropospheric_maps_directory: Path | None = None
    tropospheric_map_grid_resolution: TroposphericGRIDResolution = TroposphericGRIDResolution.FINE
    etad_product_path: Path | None = None

    @classmethod
    def from_dict(cls, arg: dict) -> SCTPointTargetAnalysisConfig:
        """Creating a SCTPointTargetAnalysisConfig from a dict representing this dataclass.
        All fields except base_config are set.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        SCTPointTargetAnalysisConfig
            SCTPointTargetAnalysisConfig dataclass initialized from input dictionary
        """
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTPointTargetAnalysisConfig: {key} not supported")

            if key == "tropospheric_maps_directory":
                if value:
                    setattr(out, key, Path(value))
            elif key == "ionospheric_maps_directory":
                if value:
                    setattr(out, key, Path(value))
            elif key == "etad_product_path":
                if value:
                    setattr(out, key, Path(value))
            elif key == "ale_validity_limits":
                setattr(out, key, tuple(value))
            elif key == "ionospheric_analysis_center":
                setattr(out, key, IonosphericAnalysisCenters[value.upper()])
            elif key == "tropospheric_map_grid_resolution":
                setattr(out, key, TroposphericGRIDResolution[value.upper()])
            else:
                setattr(out, key, value)

        return out


@dataclass
class SCTRadiometricAnalysisConfig:
    """SCT Radiometric Analysis configuration"""

    base_config: RadiometricProfilesConfig = field(default_factory=RadiometricProfilesConfig)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTRadiometricAnalysisConfig:
        """Creating an SCTRadiometricAnalysisConfig form a dict representing this dataclass.
        All fields except base_config are set.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        SCTRadiometricAnalysisConfig
            SCTRadiometricAnalysisConfig dataclass initialized from input dictionary
        """
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTRadiometricAnalysisConfig: {key} not supported")

            setattr(out, key, value)

        return out


@dataclass
class SCTInterferometricAnalysisConfig:
    """SCT Interferometric Analysis configuration"""

    base_config: InterferometricConfig = field(default_factory=InterferometricConfig)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTInterferometricAnalysisConfig:
        """Creating a SCTInterferometricAnalysisConfig from a dict representing this dataclass.
        All fields except base_config are set.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        SCTInterferometricAnalysisConfig
            SCTInterferometricAnalysisConfig dataclass initialized from input dictionary
        """
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTInterferometricAnalysisConfig: {key} not supported")

            setattr(out, key, value)

        return out


@dataclass
class SCTConfiguration:
    """SCT Tool full Configuration"""

    general: DefaultConfiguration = field(default_factory=DefaultConfiguration)
    point_target_analysis: SCTPointTargetAnalysisConfig = field(default_factory=SCTPointTargetAnalysisConfig)
    radiometric_analysis: SCTRadiometricAnalysisConfig = field(default_factory=SCTRadiometricAnalysisConfig)
    interferometric_analysis: SCTInterferometricAnalysisConfig = field(default_factory=SCTInterferometricAnalysisConfig)

    @staticmethod
    def from_toml(file: Union[str, Path]) -> SCTConfiguration:
        """Generating an SCTConfiguration dataclass from a .toml configuration file.

        Parameters
        ----------
        file : Union[str, Path]
            path to the .toml configuration file

        Returns
        -------
        SCTConfiguration
            SCTConfiguration dataclass set from .toml file
        """
        file = Path(file)
        if not file.is_file():
            raise InvalidConfigurationFile(f"Input file {file} does not exist")

        if file.suffix != ".toml":
            raise InvalidConfigurationFile(f"Input file {file} is not a valid .toml configuration file")

        with open(file, "r", encoding="UTF-8") as f:
            config = toml.load(f)

        # validating toml
        toml_schema_validation(config)

        # general configuration
        general_config = DefaultConfiguration()
        if "general" in config:
            general_config = DefaultConfiguration.from_dict(config["general"])

        # point target analysis configuration
        pta_config = SCTPointTargetAnalysisConfig()
        if "point_target_analysis" in config:
            if "corrections" in config["point_target_analysis"]:
                pta_dict = config["point_target_analysis"].pop("corrections")
                if "ionosphere" in pta_dict:
                    pta_dict.update(pta_dict.pop("ionosphere"))
                if "troposphere" in pta_dict:
                    pta_dict.update(pta_dict.pop("troposphere"))
                pta_config = SCTPointTargetAnalysisConfig.from_dict(arg=pta_dict)
            if "advanced_configuration" in config["point_target_analysis"]:
                pta_advanced_config = config["point_target_analysis"].pop("advanced_configuration")
                config["point_target_analysis"].update(pta_advanced_config)
            if "ale_validity_limits" in config["point_target_analysis"]:
                config["point_target_analysis"]["ale_limits"] = config["point_target_analysis"].pop(
                    "ale_validity_limits"
                )
            pta_base_config = PointTargetAnalysisConfig.from_dict(arg=config["point_target_analysis"])
            pta_config.base_config = pta_base_config

        # radiometric analysis configuration
        ra_config = SCTRadiometricAnalysisConfig()
        if "radiometric_analysis" in config:
            if "advanced_configuration" in config["radiometric_analysis"]:
                ra_advanced_config = config["radiometric_analysis"].pop("advanced_configuration")
                config["radiometric_analysis"].update(ra_advanced_config)
            ra_base_config = RadiometricProfilesConfig.from_dict(arg=config["radiometric_analysis"])
            ra_config.base_config = ra_base_config

        # interferometric analysis configuration
        int_config = SCTInterferometricAnalysisConfig()
        if "interferometric_analysis" in config:
            int_base_config = InterferometricConfig.from_dict(arg=config["interferometric_analysis"])
            int_config.base_config = int_base_config

        # assembling final configuration
        config = SCTConfiguration()
        config.general = general_config
        config.point_target_analysis = pta_config
        config.radiometric_analysis = ra_config
        config.interferometric_analysis = int_config

        return config

    def dump_to_toml(self, out_file: Path, selected: str | ConfigSupportedAnalyses | None = None) -> None:
        """Dumping to disk a .toml file from the dataclass instance.

        Parameters
        ----------
        out_file : Path
            path to the output .toml file
        selected : str | ConfigSupportedAnalyses | None, optional
            selected analysis to be dumped, it can be "point_target", "radiometry", "interferometry",
            if None the whole configuration is dumped, by default None
        """

        dtc_dict = asdict(self)

        selected = ConfigSupportedAnalyses[selected.upper()] if selected is not None else None

        # assembling final dict
        conf_dict = {
            "general": dtc_dict["general"],
            "point_target_analysis": None,
            "radiometric_analysis": None,
            "interferometric_analysis": None,
        }

        if selected in (None, ConfigSupportedAnalyses.POINT_TARGET):
            # point target analysis re-ordering
            pta_dict = dtc_dict["point_target_analysis"]
            pta_base = pta_dict.pop("base_config")
            pta_ale = pta_base.pop("ale_limits")
            pta_corr = dict(
                (k, pta_dict[k])
                for k in (
                    "enable_etad_corrections",
                    "enable_solid_tides_correction",
                    "enable_plate_tectonics_correction",
                    "enable_sensor_specific_processing_corrections",
                    "enable_ionospheric_correction",
                    "enable_tropospheric_correction",
                    "etad_product_path",
                )
            )
            if pta_corr["etad_product_path"] is not None:
                pta_corr["etad_product_path"] = str(pta_corr["etad_product_path"])
            pta_iono = dict(
                (k, pta_dict[k])
                for k in (
                    "ionospheric_maps_directory",
                    "ionospheric_analysis_center",
                )
            )
            if pta_iono["ionospheric_analysis_center"] is not None:
                pta_iono["ionospheric_analysis_center"] = pta_iono["ionospheric_analysis_center"].name.lower()
            if pta_iono["ionospheric_maps_directory"] is not None:
                pta_iono["ionospheric_maps_directory"] = str(pta_iono["ionospheric_maps_directory"])
            pta_tropo = dict(
                (k, pta_dict[k])
                for k in (
                    "tropospheric_maps_directory",
                    "tropospheric_map_grid_resolution",
                )
            )
            if pta_tropo["tropospheric_map_grid_resolution"] is not None:
                pta_tropo["tropospheric_map_grid_resolution"] = pta_tropo[
                    "tropospheric_map_grid_resolution"
                ].name.lower()
            if pta_tropo["tropospheric_maps_directory"] is not None:
                pta_tropo["tropospheric_maps_directory"] = str(pta_tropo["tropospheric_maps_directory"])
            pta_irf = pta_base.pop("irf_parameters")
            if pta_irf["masking_method"] is not None:
                pta_irf["masking_method"] = pta_irf["masking_method"].name.lower()
            pta_rcs = pta_base.pop("rcs_parameters")
            pta_base = dict(
                (k, pta_base[k])
                for k in (
                    "perform_irf",
                    "perform_rcs",
                    "evaluate_pslr",
                    "evaluate_islr",
                    "evaluate_sslr",
                    "evaluate_localization",
                )
            )
            pta_base["ale_validity_limits"] = pta_ale
            pta_base["corrections"] = pta_corr
            if any([v is not None for v in pta_iono.values()]):
                pta_base["corrections"]["ionosphere"] = pta_iono
            if pta_tropo["tropospheric_maps_directory"] is not None:
                pta_base["corrections"]["troposphere"] = pta_tropo
            pta_base["advanced_configuration"] = {}
            pta_base["advanced_configuration"]["irf_parameters"] = pta_irf
            pta_base["advanced_configuration"]["rcs_parameters"] = pta_rcs

            # saving to configuration dict to be dumped
            conf_dict["point_target_analysis"] = pta_base

        if selected in (None, ConfigSupportedAnalyses.RADIOMETRY):
            # radiometric analysis re-ordering
            ra_dict = dtc_dict["radiometric_analysis"]["base_config"]
            ra_hist_params = ra_dict.pop("histogram_parameters")
            ra_prof_params = ra_dict.pop("profile_extraction_parameters")
            ra_dict["input_quantity"] = ra_dict["input_quantity"].name.lower()
            ra_dict["advanced_configuration"] = {}
            ra_dict["advanced_configuration"]["histogram_parameters"] = ra_hist_params
            ra_dict["advanced_configuration"]["profile_extraction_parameters"] = ra_prof_params

            # saving to configuration dict to be dumped
            conf_dict["radiometric_analysis"] = ra_dict

        if selected in (None, ConfigSupportedAnalyses.INTERFEROMETRY):
            # interferometric analysis re-ordering
            inter_dict = dtc_dict["interferometric_analysis"]["base_config"]

            if not isinstance(inter_dict["coherence_kernel"], (tuple, list)):
                inter_dict["coherence_kernel"] = (inter_dict["coherence_kernel"], inter_dict["coherence_kernel"])

            # saving to configuration dict to be dumped
            conf_dict["interferometric_analysis"] = inter_dict

        with open(out_file, "w", encoding="UTF-8") as f_out:
            toml.dump(conf_dict, f_out)
