# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Abstract Base Class for Analyses Configurations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

import toml

from sct.configuration.common import InvalidConfigurationFile, toml_schema_validation


class AnalysisConfigABC(ABC):
    """Abstract Base Class for Analyses Configurations"""

    validation_schema: Path
    config_group_name: str

    @classmethod
    @abstractmethod
    def from_dict(cls, arg: dict) -> Self:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_toml(cls, file: str | Path) -> Self:
        """Generating a Self dataclass from a .toml configuration file.

        Parameters
        ----------
        file : str | Path
            path to the .toml configuration file

        Returns
        -------
        Self
            Self dataclass set from .toml file
        """
        file = Path(file)
        if not file.is_file():
            raise InvalidConfigurationFile(f"Input file {file} does not exist")

        if file.suffix != ".toml":
            raise InvalidConfigurationFile(f"Input file {file} is not a .toml configuration file")

        with open(file, "r", encoding="UTF-8") as f:
            config = toml.load(f)

        toml_schema_validation(content=config, schema_path=cls.validation_schema)

        return cls.from_dict(config[cls.config_group_name])

    def to_toml(self, out_file: Path) -> None:
        """Saving to disk a .toml file from the dataclass instance.

        Parameters
        ----------
        out_file : Path
            path to the output .toml file
        """
        with open(out_file, "w", encoding="UTF-8") as f_out:
            toml.dump(self.to_dict(), f_out)
