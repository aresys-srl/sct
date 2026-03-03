# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Radiometric Analysis"""

from __future__ import annotations

from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.analyses.radiometry.main import (
    full_average_elevation_profiles_analysis,
    full_nesz_analysis,
)
from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams, cli_launcher

ABSOLUTE_TOLERANCE_RA = 1e-2
ABSOLUTE_TOLERANCE = 1e-5
KPI_TOLERANCE = 1e-1


def run_nesz_api(
    params: TestParams, output_dir: Path, config: SCTRadiometricAnalysisConfig | None, graphs: bool
) -> TestOutput:
    """Running SCT NESZ Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    TestOutput
        Paths to output netcdf file and kpi statistics file
    """
    nc_results, kpi_results = full_nesz_analysis(
        product=params.product,
        output_directory=output_dir,
        config=config,
        graphs=graphs,
    )
    return TestOutput(netcdf_results=nc_results, csv_results=kpi_results)


def run_rain_forest_api(
    params: TestParams, output_dir: Path, config: SCTRadiometricAnalysisConfig | None, graphs: bool
) -> TestOutput:
    """Running SCT Average Radiometric Profiles Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    TestOutput
        Paths to output netcdf file and kpi statistics file
    """
    nc_results, kpi_results = full_average_elevation_profiles_analysis(
        product=params.product,
        output_radiometric_quantity=SARRadiometricQuantity.GAMMA_NOUGHT,
        output_directory=output_dir,
        config=config,
        graphs=graphs,
    )
    return TestOutput(netcdf_results=nc_results, csv_results=kpi_results)


def run_ra_cli(params: TestParams, output_dir: Path, config: Path | None, analysis: str, graphs: bool) -> TestOutput:
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
    TestOutput
        Paths to output netcdf file and kpi statistics file

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
    cli_args = []
    if config is not None:
        cli_args.extend(["--config", config])
    cli_args.extend(
        [
            "radiometry",
            "rain-forest" if analysis == "RF" else "nesz",
            "-p",
            str(params.product),
            "-out",
            str(output_dir),
        ]
    )
    if graphs:
        cli_args.extend(["-g"])

    cli_launcher(cli_args)

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

    return TestOutput(netcdf_results=output_files_nc[0], csv_results=kpi_file)


def validate_ra_results(current_output: TestOutput, reference_output: ReferenceOutput) -> None:
    """Validating radiometric analysis NetCDF and KPI stats results.

    Parameters
    ----------
    current_output : TestOutput
        current run output
    reference_output : ReferenceOutput
        reference output
    """
    compare_ra_netcdf_with_tolerances(ref=reference_output.netcdf_reference, current=current_output.netcdf_results)
    compare_kpi_stats(ref=pd.read_csv(reference_output.csv_reference), current=pd.read_csv(current_output.csv_results))


def compare_ra_netcdf_with_tolerances(ref: Path, current: Path) -> None:
    """Compare radiometric netCDF output results with tolerances.

    Parameters
    ----------
    ref : Path
        Path to the reference netCDF4 file
    current : Path
        Path to the current run netCDF4 file
    """
    ref_dataset = Dataset(ref, "r", format="NETCDF4")
    current_dataset = Dataset(current, "r", format="NETCDF4")

    assert ref_dataset.product == current_dataset.product
    assert ref_dataset.sensor == current_dataset.sensor
    assert ref_dataset.product_type == current_dataset.product_type
    assert ref_dataset.acquisition_mode == current_dataset.acquisition_mode
    assert ref_dataset.orbit_direction == current_dataset.orbit_direction
    assert ref_dataset.acquisition_start_time == current_dataset.acquisition_start_time
    assert ref_dataset.direction == current_dataset.direction
    assert ref_dataset.output_radiometric_quantity == current_dataset.output_radiometric_quantity
    assert ref_dataset.groups.keys() == current_dataset.groups.keys()
    for key, group in ref_dataset.groups.items():
        current_group = current_dataset.groups[key]
        assert group.groups.keys() == current_group.groups.keys()
        for p_key, subgroup in group.groups.items():
            current_subgroup = current_group.groups[p_key]
            assert current_subgroup.swath == subgroup.swath
            assert current_subgroup.channel == subgroup.channel
            assert current_subgroup.polarization == subgroup.polarization
            assert subgroup.azimuth_blocks_num == current_subgroup.azimuth_blocks_num
            assert subgroup.azimuth_block_centers == current_subgroup.azimuth_block_centers

            np.testing.assert_allclose(
                subgroup.range_block_centers,
                current_subgroup.range_block_centers,
                atol=ABSOLUTE_TOLERANCE,
                rtol=0,
            )

            np.testing.assert_allclose(
                subgroup["look_angles"][:],
                current_subgroup["look_angles"][:],
                atol=ABSOLUTE_TOLERANCE,
                rtol=0,
            )
            np.testing.assert_allclose(
                subgroup["radiometric_profiles"][:],
                current_subgroup["radiometric_profiles"][:],
                atol=ABSOLUTE_TOLERANCE_RA,
                rtol=0,
            )

    ref_dataset.close()
    current_dataset.close()


def compare_kpi_stats(ref: pd.DataFrame, current: pd.DataFrame) -> None:
    """Compare kpi statistics with tolerances.

    Parameters
    ----------
    ref : pd.DataFrame
        reference kpi statistics dataframe
    current : Path
        current kpi statistics dataframe
    """
    pd.testing.assert_frame_equal(ref, current, check_exact=False, atol=KPI_TOLERANCE, rtol=0)


run_nesz_cli = partial(run_ra_cli, analysis="NESZ")
run_rain_forest_cli = partial(run_ra_cli, analysis="RF")
