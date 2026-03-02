# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT General Configuration
-------------------------
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from pathlib import Path

import toml

from sct.configuration.common import InvalidConfigurationFile, toml_schema_validation
from sct.resources import config_schema


@dataclass
class GeneralConfiguration:
    """SCT general configuration"""

    save_log: bool = True
    save_config_copy: bool = True
    toml_path: Path | None = None

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

    @classmethod
    def from_toml(cls, file: str | Path) -> GeneralConfiguration:
        """Generating a GeneralConfiguration dataclass from a .toml configuration file.

        Parameters
        ----------
        file : str | Path
            path to the .toml configuration file

        Returns
        -------
        GeneralConfiguration
            GeneralConfiguration dataclass set from .toml file
        """
        file = Path(file)
        if not file.is_file():
            raise InvalidConfigurationFile(f"Input file {file} does not exist")

        if file.suffix != ".toml":
            raise InvalidConfigurationFile(f"Input file {file} is not a .toml configuration file")

        with open(file, "r", encoding="UTF-8") as f:
            config = toml.load(f)

        toml_schema_validation(content=config, schema_path=config_schema)

        if "general" in config:
            configuration = cls.from_dict(config["general"])
        else:
            configuration = cls()

        configuration.toml_path = Path(file)
        return configuration

    def to_toml(self, out_file: Path) -> None:
        """Saving to disk a .toml file from the dataclass instance.

        Parameters
        ----------
        out_file : Path
            path to the output .toml file
        """
        with open(out_file, "w", encoding="UTF-8") as f_out:
            toml.dump(self.to_dict(), f_out)
