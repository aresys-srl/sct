# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Interferometric Analysis Implementation"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from netCDF4 import Dataset

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTConfiguration
from sct.orchestration import full_interferometric_analysis_implementation
from sct.testing.utilities.analyses.base import AnalysisHandler
from sct.testing.utilities.analyses.registry import register_analysis
from sct.testing.utilities.common import ReferenceOutput, SCTAnalyses, TestOutput, TestParams, cli_launcher

ABSOLUTE_TOLERANCE = 1e-5
ABSOLUTE_TOLERANCE_INTERF = 5


def run_interferometry_api(
    params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool
) -> TestOutput:
    """Running SCT Interferometric Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    TestOutput
        path to output netcdf file
    """
    generate_coherence_graphs = None
    if graphs:
        try:
            from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    nc_output = full_interferometric_analysis_implementation(
        product=params.product if isinstance(params.product, Path) else params.product[0],
        product_2=params.product[1] if isinstance(params.product, list) else None,
        config=config,
        output_directory=output_dir,
        graphs_func=generate_coherence_graphs,
    )
    return TestOutput(netcdf_results=nc_output)


def run_interferometry_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> TestOutput:
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
    TestOutput
        paths to output NetCDF file

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

    cli_launcher(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_interf_analysis.log").exists():
        raise RuntimeError("Missing sct_interf_analysis.log file")
    output_files_nc = list(output_dir.glob("*.nc"))
    if not len(output_files_nc) > 0:
        raise RuntimeError("No output NetCDF files found")

    return TestOutput(netcdf_results=output_files_nc[0])


def validate_interf_results(current_output: TestOutput, reference_output: ReferenceOutput) -> None:
    """Compare interferometric netCDF output results with tolerances.

    Parameters
    ----------
    current_output : TestOutput
        current run output
    reference_output : ReferenceOutput
        reference output
    """

    current_dataset = Dataset(current_output.netcdf_results, "r", format="NETCDF4")
    ref_dataset = Dataset(reference_output.netcdf_reference, "r", format="NETCDF4")

    assert ref_dataset.groups.keys() == current_dataset.groups.keys()
    for key, group in ref_dataset.groups.items():
        current_group = current_dataset.groups[key]
        assert group.groups.keys() == current_group.groups.keys()
        for p_key, subgroup in group.groups.items():
            current_subgroup = current_group.groups[p_key]
            assert subgroup.swath == current_subgroup.swath
            assert subgroup.channel == current_subgroup.channel
            assert subgroup.polarization == current_subgroup.polarization
            for burst, burst_group in subgroup.groups.items():
                current_burst_group = current_subgroup.groups[burst]

                np.testing.assert_allclose(
                    burst_group["coherence_bins"][:],
                    current_burst_group["coherence_bins"][:],
                    atol=ABSOLUTE_TOLERANCE,
                    rtol=0,
                )
                np.testing.assert_allclose(
                    burst_group["azimuth_histogram"][:],
                    current_burst_group["azimuth_histogram"][:],
                    atol=ABSOLUTE_TOLERANCE_INTERF,
                    rtol=0,
                )
                np.testing.assert_allclose(
                    burst_group["range_histogram"][:],
                    current_burst_group["range_histogram"][:],
                    atol=ABSOLUTE_TOLERANCE_INTERF,
                    rtol=0,
                )

    ref_dataset.close()
    current_dataset.close()


register_analysis(
    analysis_type=SCTAnalyses.INTERFEROMETRY,
    handler=AnalysisHandler(
        api_runner=run_interferometry_api,
        cli_runner=run_interferometry_cli,
        validator=validate_interf_results,
    ),
)
