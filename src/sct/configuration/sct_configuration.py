# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT configurations
------------------
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Literal

import toml
from perseo_quality.interferometric_analysis.config import InterferometricConfig
from perseo_quality.radiometric_analysis.block_wise.config import RadiometricProfilesConfig
from perseo_quality.tar_analysis.config import AmbiguityRatioConfig

from sct.configuration.common import InvalidConfigurationFile
from sct.configuration.point_target_analysis_configuration import SCTPointTargetAnalysisConfig
from sct.configuration.toml_validation import toml_schema_validation

ConfigSupportedAnalyses = Literal[
    "interferometric_analysis",
    "radiometric_analysis",
    "point_target_analysis",
    "spectral_analysis",
    "target_ambiguity_ratio_analysis",
]


@dataclass
class GeneralConfiguration:
    """SCT general configuration"""

    save_log: bool = True
    save_config_copy: bool = True

    @classmethod
    def from_dict(cls, arg: dict) -> GeneralConfiguration:
        """Convert from dict"""
        out = cls()
        valid_fields = [f.name for f in fields(out)]

        for key, value in arg.items():
            if key not in valid_fields:
                raise InvalidConfigurationFile(f"GeneralConfiguration: {key} not supported")

            setattr(out, key, value)

        return out

    def to_dict(self) -> dict:
        """Convert to dict"""
        return asdict(self)


@dataclass
class SCTRadiometricAnalysisConfig:
    """SCT Radiometric Analysis configuration"""

    base_config: RadiometricProfilesConfig = field(default_factory=RadiometricProfilesConfig)

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

        return ra_dict


@dataclass
class SCTInterferometricAnalysisConfig:
    """SCT Interferometric Analysis configuration"""

    base_config: InterferometricConfig = field(default_factory=InterferometricConfig)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTInterferometricAnalysisConfig:
        """Convert from dict"""
        return cls(base_config=InterferometricConfig.from_dict(arg=arg))

    def to_dict(self):
        """Convert to dict"""
        out = asdict(self.base_config)

        if not isinstance(self.base_config.coherence_kernel, (tuple, list)):
            out["coherence_kernel"] = (out["coherence_kernel"], out["coherence_kernel"])

        return out


@dataclass
class SCTSpectralAnalysisConfig:
    """SCT Spectral Analysis configuration"""

    cropping_size: tuple[int, int] = (128, 128)

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
        return asdict(self)


@dataclass
class SCTTargetAmbiguityRatioConfig:
    """SCT Target Ambiguity Ratio Analysis configuration"""

    base_config: AmbiguityRatioConfig = field(default_factory=AmbiguityRatioConfig)

    @classmethod
    def from_dict(cls, arg: dict) -> SCTTargetAmbiguityRatioConfig:
        """Convert from dict"""
        return cls(base_config=AmbiguityRatioConfig.from_dict(arg))

    def to_dict(self):
        """Convert to dict"""
        return asdict(self.base_config)


@dataclass
class SCTConfiguration:
    """SCT Tool full Configuration"""

    general: GeneralConfiguration = field(default_factory=GeneralConfiguration)
    point_target_analysis: SCTPointTargetAnalysisConfig = field(default_factory=SCTPointTargetAnalysisConfig)
    radiometric_analysis: SCTRadiometricAnalysisConfig = field(default_factory=SCTRadiometricAnalysisConfig)
    interferometric_analysis: SCTInterferometricAnalysisConfig = field(default_factory=SCTInterferometricAnalysisConfig)
    spectral_analysis: SCTSpectralAnalysisConfig = field(default_factory=SCTSpectralAnalysisConfig)
    target_ambiguity_ratio_analysis: SCTTargetAmbiguityRatioConfig = field(
        default_factory=SCTTargetAmbiguityRatioConfig
    )

    @classmethod
    def from_dict(cls, config) -> SCTConfiguration:
        """Convert from dict"""
        sct_conf = cls()

        if "general" in config:
            sct_conf.general = GeneralConfiguration.from_dict(config["general"])

        if "point_target_analysis" in config:
            sct_conf.point_target_analysis = SCTPointTargetAnalysisConfig.from_dict(arg=config["point_target_analysis"])

        if "radiometric_analysis" in config:
            sct_conf.radiometric_analysis = SCTRadiometricAnalysisConfig.from_dict(arg=config["radiometric_analysis"])

        if "interferometric_analysis" in config:
            sct_conf.interferometric_analysis = SCTInterferometricAnalysisConfig.from_dict(
                arg=config["interferometric_analysis"]
            )

        if "spectral_analysis" in config:
            sct_conf.spectral_analysis = SCTSpectralAnalysisConfig.from_dict(arg=config["spectral_analysis"])

        if "ambiguity_ratio_analysis" in config:
            sct_conf.target_ambiguity_ratio_analysis = SCTTargetAmbiguityRatioConfig.from_dict(
                arg=config["ambiguity_ratio_analysis"]
            )

        return sct_conf

    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            "general": self.general.to_dict(),
            "point_target_analysis": self.point_target_analysis.to_dict(),
            "radiometric_analysis": self.radiometric_analysis.to_dict(),
            "interferometric_analysis": self.interferometric_analysis.to_dict(),
            "spectral_analysis": self.spectral_analysis.to_dict(),
            "target_ambiguity_ratio_analysis": self.target_ambiguity_ratio_analysis.to_dict(),
        }

    @classmethod
    def from_toml(cls, file: str | Path) -> SCTConfiguration:
        """Generating an SCTConfiguration dataclass from a .toml configuration file.

        Parameters
        ----------
        file : str | Path
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
            raise InvalidConfigurationFile(f"Input file {file} is not a .toml configuration file")

        with open(file, "r", encoding="UTF-8") as f:
            config = toml.load(f)

        toml_schema_validation(config)

        return cls.from_dict(config)

    def dump_to_toml(self, out_file: Path, selected: ConfigSupportedAnalyses | None = None) -> None:
        """Dumping to disk a .toml file from the dataclass instance.

        Parameters
        ----------
        out_file : Path
            path to the output .toml file
        selected : ConfigSupportedAnalyses | None, optional
            selected analysis to be dumped, it can be "point_target", "radiometry", "interferometry",
            "spectral_analysis" or "target_ambiguity_ratio"
            if None the whole configuration is dumped, by default None
        """

        def select_sections(data: dict, selected: ConfigSupportedAnalyses | None):
            if selected is None:
                return data
            return {"general": data["general"], selected: data[selected]}

        configuration_dict = select_sections(self.to_dict(), selected)

        with open(out_file, "w", encoding="UTF-8") as f_out:
            toml.dump(configuration_dict, f_out)
