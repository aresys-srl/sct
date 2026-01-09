# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Utilities
---------------------------------
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np
import pandas as pd
from netCDF4 import Dataset
from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
from perseo_quality.elevation_notch_analysis.support import elevation_notch_profiles_to_netcdf
from perseo_quality.interferometric_analysis.support import (
    coherence_histograms_to_netcdf,
)
from perseo_quality.radiometric_analysis.block_wise.support import (
    radiometric_profiles_to_netcdf,
    radiometric_statistical_analysis_to_df,
)

from sct.analyses.elevation_notch import sct_elevation_notch_analysis
from sct.analyses.interferometric_analysis import interferometric_coherence_analysis
from sct.analyses.point_target_analysis import point_target_analysis_with_corrections
from sct.analyses.radiometric_analysis import (
    average_elevation_profile_analysis,
    nesz_analysis,
)
from sct.configuration.logger import sct_logger
from sct.configuration.point_target_analysis_configuration import (
    IonosphericCorrectionsConf,
    TroposphericCorrectionsConf,
)
from sct.configuration.sct_configuration import (
    SCTConfiguration,
    SCTElevationNotchAnalysisConfig,
    SCTInterferometricAnalysisConfig,
    SCTPointTargetAnalysisConfig,
    SCTRadiometricAnalysisConfig,
)

PYTHON_INTERPRETER = sys.executable

# TODO: configure these from CLI call using a configuration file?
ABSOLUTE_TOLERANCE = 1e-5
ABSOLUTE_TOLERANCE_SLR = 0.5
ABSOLUTE_TOLERANCE_LOC = 1e-4
ABSOLUTE_TOLERANCE_DEG = 5e-4
ABSOLUTE_TOLERANCE_RCS = 0.1
ABSOLUTE_TOLERANCE_RA = 1e-2
ABSOLUTE_TOLERANCE_OTHER = 1e-3
ABSOLUTE_TOLERANCE_INTERF = 5
KPI_TOLERANCE = 1e-1

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


def compare_pta_df_with_tolerances(ref: pd.DataFrame, current: pd.DataFrame) -> None:
    """Comparing reference dataframe and current one, column by column to assess differences in values.
    Some values are grouped by theme ad compared with specific tolerances.

    Parameters
    ----------
    ref : pd.DataFrame
        reference dataframe
    current : pd.DataFrame
        current evaluated dataframe
    """
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
        atol=ABSOLUTE_TOLERANCE_RA,
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

    assert ref_dataset.swath == current_dataset.swath
    assert ref_dataset.channel == current_dataset.channel
    assert ref_dataset.polarization == current_dataset.polarization
    assert ref_dataset.direction == current_dataset.direction
    assert ref_dataset.output_radiometric_quantity == current_dataset.output_radiometric_quantity
    assert ref_dataset.azimuth_blocks_num == current_dataset.azimuth_blocks_num
    assert ref_dataset.azimuth_block_centers == current_dataset.azimuth_block_centers

    np.testing.assert_allclose(
        ref_dataset.range_block_centers,
        current_dataset.range_block_centers,
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )

    np.testing.assert_allclose(
        ref_dataset["look_angles"][:],
        current_dataset["look_angles"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["radiometric_profiles"][:],
        current_dataset["radiometric_profiles"][:],
        atol=ABSOLUTE_TOLERANCE_RA,
        rtol=0,
    )

    ref_dataset.close()
    current_dataset.close()


def compare_interf_netcdf_with_tolerances(ref: Path, current: Path) -> None:
    """Compare interferometric netCDF output results with tolerances.

    Parameters
    ----------
    ref : Path
        Path to the reference netCDF4 file
    current : Path
        Path to the current run netCDF4 file
    """
    ref_dataset = Dataset(ref, "r", format="NETCDF4")
    current_dataset = Dataset(current, "r", format="NETCDF4")

    assert ref_dataset.swath == current_dataset.swath
    assert ref_dataset.channel == current_dataset.channel
    assert ref_dataset.polarization == current_dataset.polarization
    assert ref_dataset.burst == current_dataset.burst

    np.testing.assert_allclose(
        ref_dataset["coherence_bins"][:],
        current_dataset["coherence_bins"][:],
        atol=ABSOLUTE_TOLERANCE,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["azimuth_histogram"][:],
        current_dataset["azimuth_histogram"][:],
        atol=ABSOLUTE_TOLERANCE_INTERF,
        rtol=0,
    )
    np.testing.assert_allclose(
        ref_dataset["range_histogram"][:],
        current_dataset["range_histogram"][:],
        atol=ABSOLUTE_TOLERANCE_INTERF,
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


def compare_elevation_notch_netcdf_with_tolerances(ref: Path, current: Path) -> None:
    """Compare elevation notch netCDF output results with tolerances.

    Parameters
    ----------
    ref : Path
        Path to the reference netCDF4 file
    current : Path
        Path to the current run netCDF4 file
    """

    reference_ds = Dataset(ref, "r", format="NETCDF4")
    current_ds = Dataset(current, "r", format="NETCDF4")

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


def validate_ra_results(
    reference_output: Path | list[Path], current_nc_output: list[Path], current_kpi_stats: Path
) -> None:
    """Validating radiometric analysis NetCDF and KPI stats results.

    Parameters
    ----------
    reference_output : Path | list[Path]
        reference netCDF or KPI stats files
    current_nc_output : list[Path]
        current run netCDF files
    current_kpi_stats : Path
        current run KPI stats file
    """
    if isinstance(reference_output, list):
        for report in reference_output:
            if ".nc" in report.name:
                result = [r for r in current_nc_output if "_".join(report.name.split("_")[-3:]) in r.name]
                compare_ra_netcdf_with_tolerances(ref=report, current=result[0])
    else:
        compare_ra_netcdf_with_tolerances(ref=reference_output, current=current_nc_output[0])
    kpi_csv_file = [p for p in reference_output if ".csv" in p.name]
    if kpi_csv_file:
        compare_kpi_stats(ref=pd.read_csv(kpi_csv_file[0]), current=pd.read_csv(current_kpi_stats))


def run_pta_api(
    params: TestParams, output_dir: Path, config: SCTPointTargetAnalysisConfig | None, graphs: bool
) -> pd.DataFrame:
    """Running SCT Point Target Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTPointTargetAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    pd.DataFrame
        results dataframe
    """
    if params.ionospheric_maps is not None:
        config.corrections.enable_ionospheric_correction = True
        config.corrections.ionosphere = IonosphericCorrectionsConf(
            maps_directory=params.ionospheric_maps,
            analysis_center=config.corrections.ionosphere.analysis_center,
        )
    if params.tropospheric_maps is not None:
        config.corrections.enable_tropospheric_correction = True
        config.corrections.troposphere = TroposphericCorrectionsConf(maps_directory=params.tropospheric_maps)
    results_df, graphs_data = point_target_analysis_with_corrections(
        product_path=params.product,
        external_target_source=params.targets,
        external_orbit_path=params.external_orbit,
        external_corrections_product=params.external_corrections_product
        if params.external_corrections_product is not None
        else None,
        config=config,
    )
    out_file = output_dir.joinpath("pta_results.csv")
    results_df.to_csv(out_file, index=False)
    if graphs:
        try:
            from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation

            sct_logger.info("Plotting graphs...")
            graphs_out_dir = output_dir.joinpath("graphs")
            graphs_out_dir.mkdir(exist_ok=True)
            point_target_graphs_generation(graphs_data=graphs_data, results_df=results_df, output_dir=graphs_out_dir)
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return pd.read_csv(out_file)


def run_nesz_api(
    params: TestParams, output_dir: Path, config: SCTRadiometricAnalysisConfig | None, graphs: bool
) -> tuple[list[Path], Path]:
    """Running SCT NESZ Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTRadiometricAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    list[Path]
        paths to output netcdf files
    Path
        path to the kpi statistics file
    """
    profiles = nesz_analysis(product_path=params.product, config=config)
    stats_df = radiometric_statistical_analysis_to_df(data=profiles)
    kpi_file = output_dir.joinpath("kpi_stats.csv")
    stats_df.to_csv(kpi_file, index=False)
    tag = "NESZ"
    if graphs:
        try:
            from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            graphs = False
    for item in profiles:
        radiometric_profiles_to_netcdf(data=item, out_path=output_dir, tag=tag)
        if graphs:
            radiometric_2D_hist_plot(
                data=item,
                out_dir=output_dir,
                title=f"{tag.upper()} Profiles {item.general_info.channel}",
                plot_mode="min",
            )
    return list(output_dir.glob("*.nc")), kpi_file


def run_rain_forest_api(
    params: TestParams, output_dir: Path, config: SCTRadiometricAnalysisConfig | None, graphs: bool
) -> tuple[list[Path], Path]:
    """Running SCT Average Radiometric Profiles Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTRadiometricAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    list[Path]
        paths to output netcdf files
    Path
        path to the kpi statistics file
    """
    profiles = average_elevation_profile_analysis(
        product_path=params.product,
        output_quantity=SARRadiometricQuantity.GAMMA_NOUGHT,
        config=config,
    )
    stats_df = radiometric_statistical_analysis_to_df(data=profiles)
    kpi_file = output_dir.joinpath("kpi_stats.csv")
    stats_df.to_csv(kpi_file, index=False)
    tag = "RAIN_FOREST"
    if graphs:
        try:
            from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            graphs = False
    for item in profiles:
        radiometric_profiles_to_netcdf(data=item, out_path=output_dir, tag=tag)
        if graphs:
            radiometric_2D_hist_plot(
                data=item,
                out_dir=output_dir,
                title=f"{tag.upper()} Profiles {item.general_info.channel}",
                plot_mode="mean",
            )
    return list(output_dir.glob("*.nc")), kpi_file


def run_interferometry_api(
    params: TestParams, output_dir: Path, config: SCTInterferometricAnalysisConfig | None
) -> Path:
    """Running SCT Interferometric Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTInterferometricAnalysisConfig | None
        configuration

    Returns
    -------
    Path
        path to output netcdf file
    """
    first_prod = params.product if isinstance(params.product, Path) else params.product[0]
    second_prod = params.product[1] if isinstance(params.product, list) else None
    coherence_res = interferometric_coherence_analysis(
        product_path=first_prod, second_product_path=second_prod, config=config
    )
    for res in coherence_res:
        # saving 2D histograms to netcdf
        coherence_histograms_to_netcdf(data=res, output_dir=output_dir)
    return [output_dir.joinpath(p.name) for p in params.reference_output]


def run_elevation_notch_api(
    params: TestParams, output_dir: Path, config: SCTElevationNotchAnalysisConfig | None, graphs: bool
) -> Path:
    """Running SCT Elevation Notch Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTElevationNotchAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to output netcdf file
    """
    results = sct_elevation_notch_analysis(
        product_path=params.product,
        antenna_pattern_file=params.antenna_pattern,
        config=config,
    )
    if graphs:
        try:
            from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis

            plot_elevation_notch_analysis(data=results, output_dir=output_dir)
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return elevation_notch_profiles_to_netcdf(data=results, output_dir=output_dir)


def run_pta_cli(params: TestParams, output_dir: Path, config: Path | None, graphs: bool) -> pd.DataFrame:
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
    pd.DataFrame
        results dataframe

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

    return pd.read_csv(output_files[0])


def run_ra_cli(
    params: TestParams, output_dir: Path, config: Path | None, analysis: str, graphs: bool
) -> tuple[list[Path], Path]:
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
    list[Path]
        paths to output netcdf files
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
    if not len(output_files_nc) > 0:
        raise RuntimeError("No output NetCDF files found")
    if not kpi_file.exists():
        raise RuntimeError("Missing radiometry_statistics.csv file")

    return output_files_nc, kpi_file


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

    return output_files_nc


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


def dump_sct_config(config: SCTConfiguration | None, out_path: Path) -> None:
    """Saving input config to disk.

    Parameters
    ----------
    config : SCTConfiguration | None
        input config, if any
    out_path : Path
        path to the file on disk where to save the config
    """
    assert str(out_path).endswith(".json")
    out_config = config or SCTConfiguration()
    out_config.dump_to_toml(out_file=out_path)


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
