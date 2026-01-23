# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Testing - Validation Utilities
----------------------------------
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from netCDF4 import Dataset

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


def validate_ra_results(reference_output: list[Path], current_nc_output: Path, current_kpi_stats: Path) -> None:
    """Validating radiometric analysis NetCDF and KPI stats results.

    Parameters
    ----------
    reference_output : Path | list[Path]
        reference KPI and NetCDF files
    current_nc_output : Path
        current run netCDF file
    current_kpi_stats : Path
        current run KPI stats file
    """
    for report in reference_output:
        if ".nc" in report.name:
            compare_ra_netcdf_with_tolerances(ref=report, current=current_nc_output)
        elif ".csv" in report.name:
            compare_kpi_stats(ref=pd.read_csv(report), current=pd.read_csv(current_kpi_stats))
        else:
            raise ValueError(f"Unsupported report type: {report.name}")


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

    reference_ds.close()
    current_ds.close()
