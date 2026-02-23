# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Testing - Point Target Analysis Implementation"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from sct.configuration.logger import sct_logger
from sct.configuration.point_target_analysis_configuration import (
    IonosphericCorrectionsConf,
    TroposphericCorrectionsConf,
)
from sct.configuration.sct_configuration import SCTConfiguration
from sct.orchestration import full_point_target_analysis_implementation
from sct.testing.utilities.analyses.base import AnalysisHandler
from sct.testing.utilities.analyses.registry import register_analysis
from sct.testing.utilities.common import ReferenceOutput, SCTAnalyses, TestOutput, TestParams, cli_launcher

ABSOLUTE_TOLERANCE = 1e-5
ABSOLUTE_TOLERANCE_SLR = 0.5
ABSOLUTE_TOLERANCE_LOC = 1e-4
ABSOLUTE_TOLERANCE_DEG = 5e-4
ABSOLUTE_TOLERANCE_RCS = 0.1
ABSOLUTE_TOLERANCE_OTHER = 1e-2

LOC_VAR_LIST = [
    "range_resolution_[m]",
    "azimuth_resolution_[m]",
    "slant_range_localization_error_[m]",
    "azimuth_localization_error_[m]",
    "ground_range_localization_error_[m]",
    "revised_ale_range_[m]",
    "revised_ale_azimuth_[m]",
]
ADDITIONAL_LOC_VAR_LIST = ["ext_ale_range_correction_[m]", "ext_ale_azimuth_correction_[m]"]
DEG_VAR_LIST = ["incidence_angle_[deg]"]
SLR_VAR_LIST = [
    "range_islr_[dB]",
    "azimuth_islr_[dB]",
    "islr_2d_[dB]",
    "range_sslr_[dB]",
    "azimuth_sslr_[dB]",
    "sslr_2d_[dB]",
]
RCS_VAR_LIST = ["rcs_[dB]", "rcs_error_[dB]", "clutter_[dB]", "scr_[dB]", "peak_phase_error_[deg]"]
OTHER_VAR_LIST = [
    "ground_velocity_[ms]",
    "doppler_rate_theoretical_[Hzs]",
    "doppler_rate_real_[Hzs]",
    "doppler_frequency_[Hz]",
]
AZ_TIME_VAR = ["peak_azimuth_time_[UTC]"]


def run_pta_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool) -> TestOutput:
    """Running SCT Point Target Analysis from API forwarding the inputs.

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
        Path to the saved output .csv file
    """
    if params.ionospheric_maps is not None:
        config.point_target_analysis.corrections.enable_ionospheric_correction = True
        config.point_target_analysis.corrections.ionosphere = IonosphericCorrectionsConf(
            maps_directory=params.ionospheric_maps,
            analysis_center=config.point_target_analysis.corrections.ionosphere.analysis_center,
        )
    if params.tropospheric_maps is not None:
        config.point_target_analysis.corrections.enable_tropospheric_correction = True
        config.point_target_analysis.corrections.troposphere = TroposphericCorrectionsConf(
            maps_directory=params.tropospheric_maps
        )
    point_target_graphs_generation = None
    if graphs:
        try:
            from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    output_csv = full_point_target_analysis_implementation(
        product=params.product,
        external_orbit=params.external_orbit,
        external_corrections_product=params.external_corrections_product,
        point_target_source=params.targets,
        output_directory=output_dir,
        config=config,
        graphs_func=point_target_graphs_generation,
    )
    return TestOutput(csv_results=output_csv)


def run_pta_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> TestOutput:
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
    TestOutput
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
            str(params.product),
            "-out",
            str(output_dir),
            "-pt",
            str(params.targets),
        ]
    )
    if params.external_orbit is not None:
        executable_call.extend(["-eo", params.external_orbit])
    if params.external_corrections_product is not None:
        executable_call.extend(["-ec", params.external_corrections_product])
    if graphs:
        executable_call.extend(["-g"])

    cli_launcher(executable_call)

    # checking successful run
    if not output_dir.joinpath("analysis_config.toml").exists():
        raise RuntimeError("Missing analysis_config.toml file")
    if not output_dir.joinpath("sct_pta_analysis.log").exists():
        raise RuntimeError("Missing sct_pta_analysis.log file")
    output_files = list(output_dir.glob("*.csv"))
    if not len(output_files) == 1:
        raise RuntimeError("No output CSV file found")

    return TestOutput(csv_results=output_files[0])


def validate_pta_results(current_output: TestOutput, reference_output: ReferenceOutput) -> None:
    """Comparing reference dataframe and current one, column by column to assess differences in values.
    Some values are grouped and compared with specific tolerances.

    Parameters
    ----------
    current_output : TestOutput
        current run output
    reference_output : ReferenceOutput
        reference output
    """
    current = pd.read_csv(current_output.csv_results)
    ref = pd.read_csv(reference_output.csv_reference)

    # filtering only valid rows
    current = current.loc[~current["incidence_angle_[deg]"].isna()]
    current.reset_index(drop=True, inplace=True)
    ref = ref.loc[~ref["incidence_angle_[deg]"].isna()]
    ref.reset_index(drop=True, inplace=True)

    # splitting dataframes to check different values with specific tolerances
    loc_var_list = LOC_VAR_LIST
    if set(ADDITIONAL_LOC_VAR_LIST).issubset(current.columns):
        loc_var_list = LOC_VAR_LIST + ADDITIONAL_LOC_VAR_LIST
    loc_df_ref = ref[loc_var_list].copy()
    loc_report = current[loc_var_list].copy()
    pd.testing.assert_frame_equal(loc_df_ref, loc_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_LOC, rtol=0)

    deg_df_ref = ref[DEG_VAR_LIST].copy()
    deg_report = current[DEG_VAR_LIST].copy()
    pd.testing.assert_frame_equal(deg_df_ref, deg_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_DEG, rtol=0)

    islr_df_ref = ref[SLR_VAR_LIST].copy()
    islr_report = current[SLR_VAR_LIST].copy()
    pd.testing.assert_frame_equal(
        islr_df_ref,
        islr_report,
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE_SLR,
        rtol=0,
    )

    rcs_df_ref = ref[RCS_VAR_LIST].copy()
    rcs_report = current[RCS_VAR_LIST].copy()
    pd.testing.assert_frame_equal(rcs_df_ref, rcs_report, check_exact=False, atol=ABSOLUTE_TOLERANCE_RCS, rtol=0)

    other_df_ref = ref[OTHER_VAR_LIST].copy()
    other_report = current[OTHER_VAR_LIST].copy()
    pd.testing.assert_frame_equal(
        other_df_ref,
        other_report,
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE_OTHER,
        rtol=0,
    )

    # checking goodness of results
    pd.testing.assert_frame_equal(
        ref.drop(
            loc_var_list + DEG_VAR_LIST + SLR_VAR_LIST + RCS_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR,
            axis=1,
        ),
        current.drop(
            loc_var_list + DEG_VAR_LIST + SLR_VAR_LIST + RCS_VAR_LIST + OTHER_VAR_LIST + AZ_TIME_VAR,
            axis=1,
        ),
        check_exact=False,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )


register_analysis(
    analysis_type=SCTAnalyses.POINT_TARGET,
    handler=AnalysisHandler(
        api_runner=run_pta_api,
        cli_runner=run_pta_cli,
        validator=validate_pta_results,
    ),
)
