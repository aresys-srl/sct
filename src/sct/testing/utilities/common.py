# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Common Utilities"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from sct.configuration.logger import sct_logger


class SCTAnalyses(Enum):
    """Supported analyses"""

    POINT_TARGET = "pta"
    NESZ = "nesz"
    RAIN_FOREST = "rf"
    INTERFEROMETRY = "interf"
    ELEVATION_NOTCH = "notch"
    SPECTRA = "spectra"


@dataclass
class TestOutput:
    """Test output definition"""

    csv_results: Path | None = None
    netcdf_results: Path | None = None


@dataclass
class ReferenceOutput:
    """Reference output definition"""

    csv_reference: Path | None = None
    netcdf_reference: Path | None = None


@dataclass
class TestParams:
    """Tests input parameters setup"""

    analysis: SCTAnalyses | None = None
    product: Path | list[Path] | None = None
    config: Path | None = None
    targets: Path | None = None
    external_orbit: Path | None = None
    antenna_pattern: Path | None = None
    reference_output: ReferenceOutput | None = None
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
            elif key == "reference_output":
                if not isinstance(val, list):
                    val = [val]
                assert len(val) <= 2
                nc_ref = [v for v in val if str(v).endswith(".nc")]
                csv_ref = [v for v in val if str(v).endswith(".csv")]
                setattr(
                    out,
                    key,
                    ReferenceOutput(
                        csv_reference=csv_ref[0] if csv_ref else None, netcdf_reference=nc_ref[0] if nc_ref else None
                    ),
                )
            else:
                if isinstance(val, list):
                    setattr(out, key, [Path(v) for v in val])
                elif val != "":
                    setattr(out, key, Path(val))
        return out


def cli_launcher(executable_call: list[str]) -> None:
    """Launching SCT CLI interface with provided commands.

    Parameters
    ----------
    executable_call : list[str]
        executable call
    """
    process = subprocess.Popen(
        executable_call,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()
    if process.returncode != 0:
        sct_logger.critical("error: ", process.stderr)
