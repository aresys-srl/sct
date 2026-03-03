# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Elevation Notch Analysis"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig
from sct.analyses.elevation_notch.main import full_elevation_notch_analysis
from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams, cli_launcher

ABSOLUTE_TOLERANCE = 1e-5


def run_notch_api(
    params: TestParams, output_dir: Path, config: SCTElevationNotchAnalysisConfig | None, graphs: bool
) -> TestOutput:
    """Running SCT Elevation Notch Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTElevationNotchAnalysisConfig | None
        analysis configuration, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    TestOutput
        path to output netcdf file
    """
    nc_output = full_elevation_notch_analysis(
        product=params.product,
        antenna_pattern=params.antenna_pattern,
        output_directory=output_dir,
        config=config,
        graphs=graphs,
    )
    return TestOutput(netcdf_results=nc_output)


def run_notch_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> TestOutput:
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
    TestOutput
        path to NetCDF output file

    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output NetCDF results file
    """
    cli_args = []
    if config is not None:
        cli_args.extend(["--config", str(config)])
    cli_args.extend(
        [
            "elevation_notch",
            "-p",
            str(params.product),
            "-out",
            str(output_dir),
        ]
    )
    if params.antenna_pattern is not None:
        cli_args.extend(["-ap", str(params.antenna_pattern)])
    if graphs:
        cli_args.extend(["-g"])

    cli_launcher(cli_args)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_notch_analysis.log").exists():
        raise RuntimeError("Missing sct_notch_analysis.log file")
    nc_output_file = list(output_dir.glob("*.nc"))
    if not len(nc_output_file) == 1:
        raise RuntimeError("No output NetCDF file found")

    return TestOutput(netcdf_results=nc_output_file[0])


def validate_notch_results(current_output: TestOutput, reference_output: ReferenceOutput) -> None:
    """Compare elevation notch netCDF output results with tolerances.

    Parameters
    ----------
    current_output : TestOutput
        current run output
    reference_output : ReferenceOutput
        reference output
    """

    current_ds = Dataset(current_output.netcdf_results, "r", format="NETCDF4")
    reference_ds = Dataset(reference_output.netcdf_reference, "r", format="NETCDF4")

    assert reference_ds.groups.keys() == current_ds.groups.keys()
    for key, group in reference_ds.groups.items():
        current_group = current_ds.groups[key]
        assert group.groups.keys() == current_group.groups.keys()
        for s_key, subgroup in group.groups.items():
            current_subgroup = current_group.groups[s_key]
            assert subgroup.azimuth_blocks_num == current_subgroup.azimuth_blocks_num
            assert subgroup.lines_per_block == current_subgroup.lines_per_block
            assert subgroup.samples_per_block == current_subgroup.samples_per_block
            assert subgroup.variables.keys() == current_subgroup.variables.keys()
            for var_name, var in subgroup.variables.items():
                current_var = current_subgroup.variables[var_name]
                try:
                    assert var.units == current_var.units
                except AttributeError:
                    pass
                np.testing.assert_allclose(
                    var[:],
                    current_var[:],
                    atol=ABSOLUTE_TOLERANCE,
                    rtol=0,
                )

    reference_ds.close()
    current_ds.close()
