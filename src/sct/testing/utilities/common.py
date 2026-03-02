# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Common Utilities"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from click.testing import CliRunner


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

    analysis: str | None = None
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
                setattr(out, key, val)
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


def cli_launcher(cli_args: list[str]) -> None:
    from sct.cli.cli import sct_analysis

    runner = CliRunner()

    result = runner.invoke(sct_analysis, cli_args)

    assert result.exit_code == 0
