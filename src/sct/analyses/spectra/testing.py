# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Spectral Analysis"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.analyses.spectra.main import full_spectral_analysis
from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams, cli_launcher

ABSOLUTE_TOLERANCE = 1e-5


def run_spectral_api(
    params: TestParams, output_dir: Path, config: SCTSpectralAnalysisConfig | None, graphs: bool
) -> TestOutput:
    """Running SCT NESZ Analysis from API forwarding the inputs, both for Point Target and Distributed Analysis.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTSpectralAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    TestOutput
        Paths to output netcdf file and kpi statistics file
    """
    nc_results = full_spectral_analysis(
        product=params.product,
        point_target_source=params.targets,
        output_directory=output_dir,
        config=config,
        graphs=graphs,
    )
    return TestOutput(netcdf_results=nc_results)


def run_spectral_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> TestOutput:
    """Running SCT Spectral Analysis using CLI tool forwarding the inputs, both for Point Target and Distributed
    Analysis.

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
        Paths to output netcdf file

    Raises
    ------
    RuntimeError
        if missing output configuration file
    RuntimeError
        if missing output log file
    RuntimeError
        if missing output NetCDF files
    """
    cli_args = []
    if config is not None:
        cli_args.extend(["--config", str(config)])
    cli_args.extend(
        [
            "spectra",
            "-p",
            str(params.product),
            "-out",
            str(output_dir),
        ]
    )
    if params.targets is not None:
        cli_args.extend(
            [
                "-pt",
                str(params.targets),
            ]
        )
    if graphs:
        cli_args.extend(["-g"])

    cli_launcher(cli_args)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_spectral_analysis.log").exists():
        raise RuntimeError("Missing sct_spectral_analysis.log file")
    output_files_nc = list(output_dir.glob("*.nc"))
    if not output_files_nc:
        raise RuntimeError("No output NetCDF files found")
    if len(output_files_nc) > 1:
        raise RuntimeError("More than one output NetCDF file found")

    return TestOutput(netcdf_results=output_files_nc[0])


def validate_spectral_results(current_output: TestOutput, reference_output: ReferenceOutput) -> None:
    """Compare spectral analysis profiles netCDF output results with tolerances.

    Parameters
    ----------
    current_output : TestOutput
        current run output
    reference_output : ReferenceOutput
        reference output
    """
    current_dataset = Dataset(current_output.netcdf_results, "r", format="NETCDF4")
    ref_dataset = Dataset(reference_output.netcdf_reference, "r", format="NETCDF4")

    assert ref_dataset.product == current_dataset.product
    assert ref_dataset.sensor == current_dataset.sensor
    assert ref_dataset.product_type == current_dataset.product_type
    assert ref_dataset.acquisition_mode == current_dataset.acquisition_mode
    assert ref_dataset.orbit_direction == current_dataset.orbit_direction
    assert ref_dataset.groups.keys() == current_dataset.groups.keys()
    for key, group in ref_dataset.groups.items():
        current_group = current_dataset.groups[key]
        assert group.groups.keys() == current_group.groups.keys()
        for p_key, subgroup in group.groups.items():
            current_subgroup = current_group.groups[p_key]
            assert current_subgroup.swath == subgroup.swath
            assert current_subgroup.channel == subgroup.channel
            assert current_subgroup.polarization == subgroup.polarization
            assert current_subgroup.acquisition_start_time == subgroup.acquisition_start_time
            assert sorted(current_subgroup.variables.keys()) == sorted(subgroup.variables.keys())
            np.testing.assert_array_equal(
                subgroup.bursts,
                current_subgroup.bursts,
            )
            for var_key, var in subgroup.variables.items():
                np.testing.assert_allclose(
                    var[:],
                    current_subgroup[var_key][:],
                    atol=ABSOLUTE_TOLERANCE,
                    rtol=0,
                )

    current_dataset.close()
    ref_dataset.close()
