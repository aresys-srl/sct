# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Utilities
---------------------------------
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd

from sct.configuration.logger import sct_logger
from sct.testing.utilities.common import SCTAnalyses, TestParams
from sct.testing.utilities.validation import (
    compare_elevation_notch_netcdf_with_tolerances,
    compare_interf_netcdf_with_tolerances,
    compare_pta_df_with_tolerances,
    validate_ra_results,
)


def cli_testing(test_params: TestParams, output_dir: Path, graphs: bool = False):
    """SCT CLI testing routine."""
    match test_params.analysis:
        case SCTAnalyses.POINT_TARGET:
            results = run_pta_cli(params=test_params, output_dir=output_dir, config=test_params.config, graphs=graphs)
            # comparing dataframes differences to specific tolerances
            sct_logger.info("Validating results...")
            compare_pta_df_with_tolerances(ref=pd.read_csv(test_params.reference_output), current=pd.read_csv(results))
        case SCTAnalyses.NESZ:
            nc_results, kpi_results = run_ra_cli(
                params=test_params, output_dir=output_dir, config=test_params.config, analysis="NESZ", graphs=graphs
            )
            sct_logger.info("Validating results...")
            validate_ra_results(
                reference_output=test_params.reference_output,
                current_nc_output=nc_results,
                current_kpi_stats=kpi_results,
            )
        case SCTAnalyses.RAIN_FOREST:
            nc_results, kpi_results = run_ra_cli(
                params=test_params, output_dir=output_dir, config=test_params.config, analysis="RF", graphs=graphs
            )
            sct_logger.info("Validating results...")
            validate_ra_results(
                reference_output=test_params.reference_output,
                current_nc_output=nc_results,
                current_kpi_stats=kpi_results,
            )
        case SCTAnalyses.INTERFEROMETRY:
            nc_results = run_interferometry_cli(
                params=test_params, output_dir=output_dir, config=test_params.config, graphs=graphs
            )
            sct_logger.info("Validating results...")
            compare_interf_netcdf_with_tolerances(ref=test_params.reference_output, current=nc_results)
        case SCTAnalyses.ELEVATION_NOTCH:
            nc_results = run_notch_cli(
                params=test_params, output_dir=output_dir, config=test_params.config, graphs=graphs
            )
            sct_logger.info("Validating results...")
            compare_elevation_notch_netcdf_with_tolerances(ref=test_params.reference_output, current=nc_results)
        case _:
            raise ValueError(f"Unsupported analysis type: {test_params.analysis}")


def run_pta_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> Path:
    """Running SCT Point Target Analysis using CLI tool forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : Path | None
        configuration file
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the CSV file containing the point target analysis results

    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output analysis results csv file
    """
    executable_call = ["sct"]
    if config is not None:
        executable_call.extend(["--config", config])
    executable_call.extend(
        [
            "target-analysis",
            "-p",
            params.product,
            "-out",
            output_dir,
            "-pt",
            params.targets,
        ]
    )
    if params.external_orbit is not None:
        executable_call.extend(["-eo", params.external_orbit])
    if params.external_corrections_product is not None:
        executable_call.extend(["-ec", params.external_corrections_product])
    if graphs:
        executable_call.extend(["-g"])

    _launch_cli_interface(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_pta_analysis.log").exists():
        raise RuntimeError("Missing sct_pta_analysis.log file")
    output_files = list(output_dir.glob("*.csv"))
    if not len(output_files) == 1:
        raise RuntimeError("No output CSV file found")

    return output_files[0]


def run_ra_cli(
    params: TestParams, output_dir: Path, config: Path | None, analysis: str, graphs: bool
) -> tuple[Path, Path]:
    """Running SCT Radiometric Analysis using CLI tool forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : Path | None
        configuration file
    analysis : str
        analysis to be performed, [NESZ, RF]
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        paths to output netcdf file
    Path
        path to the kpi statistics file

    Raises
    ------
    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output NetCDF files
    RuntimeError
        if missing output KPI statistics file
    """
    executable_call = ["sct"]
    if config is not None:
        executable_call.extend(["--config", config])
    executable_call.extend(
        [
            "radiometric-analysis",
            "elevation-profile" if analysis == "RF" else "nesz",
            "-p",
            params.product,
            "-out",
            output_dir,
        ]
    )
    if analysis == "RF":
        executable_call.extend(
            [
                "-r",
                "gamma",
            ]
        )
    if graphs:
        executable_call.extend(["-g"])

    _launch_cli_interface(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_ra_analysis.log").exists():
        raise RuntimeError("Missing sct_ra_analysis.log file")
    output_files_nc = list(output_dir.glob("*.nc"))
    kpi_file = output_dir.joinpath("radiometry_statistics.csv")
    if not output_files_nc:
        raise RuntimeError("No output NetCDF files found")
    if len(output_files_nc) > 1:
        raise RuntimeError("More than one output NetCDF file found")
    if not kpi_file.exists():
        raise RuntimeError("Missing radiometry_statistics.csv file")

    return output_files_nc[0], kpi_file


def run_interferometry_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> list[Path]:
    """Running SCT interferometric Analysis using CLI tool forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : Path | None
        configuration file
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    list[Path]
        list of paths to output NetCDF files

    Raises
    ------
    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output NetCDF files
    """
    first_prod = params.product if isinstance(params.product, Path) else params.product[0]
    second_prod = params.product[1] if isinstance(params.product, list) else None
    executable_call = ["sct"]
    if config is not None:
        executable_call.extend(["--config", config])
    executable_call.extend(
        [
            "interferometric-analysis",
            "-p",
            first_prod,
        ]
    )
    if second_prod is not None:
        executable_call.extend(["-pp", second_prod])
    executable_call.extend(
        [
            "-out",
            output_dir,
        ]
    )
    if graphs:
        executable_call.extend(["-g"])

    _launch_cli_interface(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_interf_analysis.log").exists():
        raise RuntimeError("Missing sct_interf_analysis.log file")
    output_files_nc = list(output_dir.glob("*.nc"))
    if not len(output_files_nc) > 0:
        raise RuntimeError("No output NetCDF files found")

    return output_files_nc[0]


def run_notch_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> Path:
    """Running SCT Elevation Notch Analysis using CLI tool forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : Path | None
        configuration file
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to NetCDF output file

    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output NetCDF results file
    """
    executable_call = ["sct"]
    if config is not None:
        executable_call.extend(["--config", config])
    executable_call.extend(
        [
            "notch-analysis",
            "-p",
            params.product,
            "-out",
            output_dir,
        ]
    )
    if params.antenna_pattern is not None:
        executable_call.extend(["-ap", params.antenna_pattern])
    if graphs:
        executable_call.extend(["-g"])

    _launch_cli_interface(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_notch_analysis.log").exists():
        raise RuntimeError("Missing sct_notch_analysis.log file")
    output_file = list(output_dir.glob("*.nc"))
    if not len(output_file) == 1:
        raise RuntimeError("No output NetCDF file found")

    return output_file[0]


def _launch_cli_interface(executable_call: list[str]) -> None:
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
