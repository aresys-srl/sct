# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Tool and analyses configuration options
---------------------------------------
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Union

import appdirs
import toml
from arepyextras.perturbations.atmospheric.ionosphere import (
    IonosphericAnalysisCenters,
    TECMappingFunctionIncidenceAngleMethod,
)
from arepyextras.perturbations.atmospheric.troposphere import TroposphericGRIDResolution
from arepyextras.quality.nesz_analysis.custom_dataclasses import NESZConfig
from arepyextras.quality.point_targets_analysis.custom_dataclasses import (
    PointTargetAnalysisConfig,
)
from arepyextras.quality.radiometric_analysis.custom_dataclasses import (
    RadiometricAnalysisConfig,
)
from jsonschema import validate

from sct import config_schema

USER_AREPYEXTRAS_QUALITY_CONFIG_FILE = Path(appdirs.user_config_dir(), "SCT_TOOL", "sct_tool_default_config.toml")
ENVIRONMENT_VARIABLE = "SCT_CONFIG_FILE"

# syncing with logger
log = logging.getLogger("quality_analysis")


class InvalidConfigurationFile(RuntimeError):
    """Invalid SCT .toml configuration file"""


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

    use_internal_db: bool = True


@dataclass
class SCTPointTargetAnalysisConfig:
    """SCT Point Target Analysis configuration"""

    base_config: PointTargetAnalysisConfig = field(default_factory=PointTargetAnalysisConfig)
    ale_validity_limits: tuple[float, float] = None  # in meters
    enable_etad_corrections: bool = True
    enable_solid_tides_correction: bool = True
    enable_plate_tectonics_correction: bool = True
    enable_sensor_specific_processing_corrections: bool = True
    enable_ionospheric_correction: bool = False
    enable_tropospheric_correction: bool = False
    ionospheric_maps_directory: Path = None
    ionospheric_analysis_center: IonosphericAnalysisCenters = None
    ionospheric_tec_inc_angle_method: TECMappingFunctionIncidenceAngleMethod = (
        TECMappingFunctionIncidenceAngleMethod.GROUND_CONVERTED
    )
    tropospheric_maps_directory: Path = None
    tropospheric_map_grid_resolution: TroposphericGRIDResolution = TroposphericGRIDResolution.FINE
    etad_product_path: Path = None

    @staticmethod
    def from_dict(arg: dict) -> SCTPointTargetAnalysisConfig:
        """Creating an SCTPointTargetAnalysisConfig form a dict representing this dataclass.
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
        out = SCTPointTargetAnalysisConfig()
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

    base_config: RadiometricAnalysisConfig = field(default_factory=RadiometricAnalysisConfig)

    @staticmethod
    def from_dict(arg: dict) -> SCTRadiometricAnalysisConfig:
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
        out = SCTRadiometricAnalysisConfig()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTRadiometricAnalysisConfig: {key} not supported")

            setattr(out, key, value)

        return out


@dataclass
class SCTNoiseEquivalentSigmaZeroConfig:
    """SCT Noise Equivalent Sigma Zero (NESZ) Analysis configuration"""

    base_config: NESZConfig = field(default_factory=NESZConfig)

    @staticmethod
    def from_dict(arg: dict) -> SCTNoiseEquivalentSigmaZeroConfig:
        """Creating an SCTNoiseEquivalentSigmaZeroConfig form a dict representing this dataclass.
        All fields except base_config are set.

        Parameters
        ----------
        arg : dict
            dict representing this dataclass

        Returns
        -------
        SCTNoiseEquivalentSigmaZeroConfig
            SCTNoiseEquivalentSigmaZeroConfig dataclass initialized from input dictionary
        """
        out = SCTNoiseEquivalentSigmaZeroConfig()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"SCTNoiseEquivalentSigmaZeroConfig: {key} not supported")

            setattr(out, key, value)

        return out


@dataclass
class SCTConfiguration:
    """SCT Tool full Configuration"""

    general: DefaultConfiguration = field(default_factory=DefaultConfiguration)
    point_target_analysis: SCTPointTargetAnalysisConfig = field(default_factory=SCTPointTargetAnalysisConfig)
    radiometric_analysis: SCTRadiometricAnalysisConfig = field(default_factory=SCTRadiometricAnalysisConfig)
    nesz_analysis: SCTNoiseEquivalentSigmaZeroConfig = field(default_factory=SCTNoiseEquivalentSigmaZeroConfig)

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

        # point target analysis configuration
        pta_config = SCTPointTargetAnalysisConfig()
        if "point_target_analysis" in config:
            if "corrections" in config["point_target_analysis"]:
                pta_dict = config["point_target_analysis"].pop("corrections")
                if "ionosphere" in pta_dict:
                    pta_dict.update(pta_dict.pop("ionosphere"))
                if "troposphere" in pta_dict:
                    pta_dict.update(pta_dict.pop("troposphere"))
                if "ale_validity_limits" in config["point_target_analysis"]:
                    pta_dict["ale_validity_limits"] = config["point_target_analysis"].pop("ale_validity_limits")
                pta_config = SCTPointTargetAnalysisConfig.from_dict(arg=pta_dict)
            if "advanced_configuration" in config["point_target_analysis"]:
                pta_advanced_config = config["point_target_analysis"].pop("advanced_configuration")
                config["point_target_analysis"].update(pta_advanced_config)
            pta_base_config = PointTargetAnalysisConfig.from_dict(arg=config["point_target_analysis"])
            pta_config.base_config = pta_base_config

        # radiometric analysis configuration
        ra_config = SCTRadiometricAnalysisConfig()
        if "radiometric_analysis" in config:
            if "advanced_configuration" in config["radiometric_analysis"]:
                ra_advanced_config = config["radiometric_analysis"].pop("advanced_configuration")
                config["radiometric_analysis"].update(ra_advanced_config)
            ra_base_config = RadiometricAnalysisConfig.from_dict(arg=config["radiometric_analysis"])
            ra_config.base_config = ra_base_config

        # nesz analysis configuration
        nesz_config = SCTNoiseEquivalentSigmaZeroConfig()
        if "nesz_analysis" in config:
            if "advanced_configuration" in config["nesz_analysis"]:
                nesz_advanced_config = config["nesz_analysis"].pop("advanced_configuration").pop("parameters")
                config["nesz_analysis"].update(nesz_advanced_config)
            nesz_base_config = NESZConfig.from_dict(arg=config["nesz_analysis"])
            nesz_config.base_config = nesz_base_config

        # assembling final configuration
        config = SCTConfiguration()
        config.point_target_analysis = pta_config
        config.radiometric_analysis = ra_config
        config.nesz_analysis = nesz_config

        return config

    def dump_to_toml(self, out_file: Path) -> None:
        """Dumping to disk a .toml file from the dataclass instance.

        Parameters
        ----------
        out_file : Path
            path to the output .toml file
        """

        dtc_dict = asdict(self)

        # point target analysis re-ordering
        pta_dict = dtc_dict["point_target_analysis"]
        pta_base = pta_dict.pop("base_config")
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
        pta_iono = dict(
            (k, pta_dict[k])
            for k in (
                "ionospheric_maps_directory",
                "ionospheric_analysis_center",
                "ionospheric_tec_inc_angle_method",
            )
        )
        if pta_iono["ionospheric_analysis_center"] is not None:
            pta_iono["ionospheric_analysis_center"] = pta_iono["ionospheric_analysis_center"].name.lower()
        if pta_iono["ionospheric_tec_inc_angle_method"] is not None:
            pta_iono["ionospheric_tec_inc_angle_method"] = pta_iono["ionospheric_tec_inc_angle_method"].name.lower()
        pta_tropo = dict(
            (k, pta_dict[k])
            for k in (
                "tropospheric_maps_directory",
                "tropospheric_map_grid_resolution",
            )
        )
        if pta_tropo["tropospheric_map_grid_resolution"] is not None:
            pta_tropo["tropospheric_map_grid_resolution"] = pta_tropo["tropospheric_map_grid_resolution"].name.lower()
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
        pta_base["corrections"] = pta_corr
        pta_base["corrections"]["ionosphere"] = pta_iono
        pta_base["corrections"]["troposphere"] = pta_tropo
        pta_base["advanced_configuration"] = {}
        pta_base["advanced_configuration"]["irf_parameters"] = pta_irf
        pta_base["advanced_configuration"]["rcs_parameters"] = pta_rcs

        # radiometric analysis re-ordering
        ra_dict = dtc_dict["radiometric_analysis"]["base_config"]
        ra_params = ra_dict.pop("parameters")
        ra_dict["input_type"] = ra_dict["input_type"].name.lower()
        ra_dict["output_type"] = ra_dict["output_type"].name.lower()
        ra_dict["value"] = ra_dict["value"].name.lower()
        ra_dict["direction"] = ra_dict["direction"].name.lower()
        ra_dict["axis"] = ra_dict["axis"].name.lower()
        ra_dict["advanced_configuration"] = {}
        ra_dict["advanced_configuration"]["parameters"] = ra_params

        # nesz analysis re-ordering
        nesz_params = dtc_dict["nesz_analysis"]["base_config"]
        nesz_dict["incidence_compensation"] = nesz_params.pop("incidence_compensation")
        nesz_dict["advanced_configuration"] = {}
        nesz_dict["advanced_configuration"]["parameters"] = nesz_params

        # assembling final dict
        conf_dict = {
            "general": dtc_dict["general"],
            "point_target_analysis": pta_base,
            "radiometric_analysis": ra_dict,
            "nesz_analysis": nesz_dict,
        }

        with open(out_file, "w", encoding="UTF-8") as f_out:
            toml.dump(conf_dict, f_out)


def default_settings_filename(create_if_missing: bool = False) -> Path:
    """Getting the location of SCT CLI tool configuration file.

    Parameters
    ----------
    create_if_missing : bool, optional
        create the file if it is missing, by default False

    Returns
    -------
    Path
        path to the configuration toml file
    """

    filename = Path(
        os.getenv(
            key=ENVIRONMENT_VARIABLE,
            default=str(USER_AREPYEXTRAS_QUALITY_CONFIG_FILE),
        )
    )

    # creating the file if none is found
    if create_if_missing and not filename.exists():
        log.info("Default configuration file is missing. Creating a new one.")
        # creating all the folder structure up to the file to be generated
        filename.parent.mkdir(exist_ok=True, parents=True)
        # dumping the SCTConfiguration with default attributes values
        default_conf = SCTConfiguration()
        default_conf.dump_to_toml(filename)
        log.info(f"Default configuration file created at: {filename}")

    return filename


if __name__ == "__main__":
    c = SCTConfiguration()
    c.dump_to_toml(r"C:\Users\giorgio.parma\Desktop\temporary_outputs\prova.toml")
