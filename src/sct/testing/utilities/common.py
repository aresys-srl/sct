# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Testing - Common Utilities
------------------------------
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SCTAnalyses(Enum):
    """Supported analyses"""

    POINT_TARGET = "pta"
    NESZ = "nesz"
    RAIN_FOREST = "rf"
    INTERFEROMETRY = "interf"
    ELEVATION_NOTCH = "notch"


@dataclass
class TestParams:
    """Tests input parameters setup"""

    analysis: SCTAnalyses | None = None
    product: Path | list[Path] | None = None
    config: Path | None = None
    targets: Path | None = None
    external_orbit: Path | None = None
    antenna_pattern: Path | None = None
    reference_output: Path | None = None
    external_corrections_product: Path | None = None
    ionospheric_maps: Path | None = None
    tropospheric_maps: Path | None = None

    @classmethod
    def from_dict(cls, arg: dict) -> TestParams:
        """Composing TestParams dataclass from config dict.

        Parameters
        ----------
        arg : dict
            input dictionary

        Returns
        -------
        TestParams
            dataclass
        """
        out = cls()
        for key, val in arg.items():
            if key == "analysis":
                setattr(out, key, SCTAnalyses(val))
            else:
                if isinstance(val, list):
                    setattr(out, key, [Path(v) for v in val])
                elif val != "":
                    setattr(out, key, Path(val))
        return out
