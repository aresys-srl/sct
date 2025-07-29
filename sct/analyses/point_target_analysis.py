# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target Analysis.
----------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

import numpy as np
import pandas as pd
from arepyextras.quality.core.signal_processing import convert_to_db
from arepyextras.quality.point_targets_analysis.analysis import point_target_analysis
from scipy.constants import speed_of_light

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core.atmospheric_corrections_main import (
    AtmosphericDelaysAcquisitionInfo,
    convert_atmospheric_delays_to_df,
    run_compute_atmospheric_delays,
)
from sct.core.etad_corrections_main import get_etad_corrections
from sct.core.geodynamics_corrections_main import run_compute_geodynamics_corrections
from sct.core.rcs_computation import compute_elevation_azimuth_wrt_enu, compute_rcs_trihedral_corner_reflector
from sct.io.io_manager import product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source

if TYPE_CHECKING:
    from arepyextras.quality.io.quality_input_protocol import ChannelData
    from arepyextras.quality.point_targets_analysis.custom_dataclasses import PointTargetGraphicalData
    from arepytools.geometry.curve_protocols import TwiceDifferentiable3DCurve

    from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct


AZIMUTH_BORE_CR = np.pi / 4
ELEV_BORE_CR = np.deg2rad(35.2644)


def _compute_theoretical_rcs_core(
    sensor_position: np.ndarray,
    target_position: np.ndarray,
    elev_bore_enu: float,
    azimuth_bore_enu: float,
    cr_arm_length: float,
    carrier_frequency_hz: float,
):
    elev_los_enu, azimuth_los_enu = compute_elevation_azimuth_wrt_enu(
        pos_cr=target_position,
        pos_sat=sensor_position,
    )

    # compute orientation of satellite in CR reference frame
    elev_los_cr = elev_los_enu - elev_bore_enu + ELEV_BORE_CR
    azimuth_los_cr = (azimuth_los_enu % (2 * np.pi)) - (azimuth_bore_enu % (2 * np.pi)) + AZIMUTH_BORE_CR

    # compute CR RCS
    # if the radio wave does not impinge on the front of the CR, the RCS computation is not valid
    is_angle_range_valid = (
        azimuth_los_cr >= 0 and azimuth_los_cr <= np.pi / 2 and elev_los_cr >= 0 and elev_los_cr <= np.pi / 2
    )
    if not is_angle_range_valid:
        return np.nan

    return convert_to_db(
        compute_rcs_trihedral_corner_reflector(
            cr_arm_length,
            speed_of_light / carrier_frequency_hz,
            elev_los_cr,
            azimuth_los_cr,
        ),
    )


def _compute_theoretical_rcs(
    data_df: pd.DataFrame,
    point_targets_df: pd.DataFrame,
    carrier_frequency_hz: float,
    trajectory: TwiceDifferentiable3DCurve,
) -> list:
    """Compute theoretical RCS for each point target in the data frame.

    Returns a list containing, for each record in data_df, the theoretical RCS computed considering the target and
    satellite positions.

    Parameters
    ----------
    data_df : pd.DataFrame
        Database of SCT analysis results
    point_targets_df : pd.DataFrame
        Database with information on each target
    carrier_frequency_hz : float
        Carrier frequency of the radar signal impinging on the target
    trajectory : TwiceDifferentiable3DCurve
        Trajectory of the satellite observing the target

    Returns
    -------
    list
        List of theoretical RCS values

    """
    results = []
    for _, row in data_df.iterrows():
        curr_point_target = point_targets_df[point_targets_df["target_name"] == row["target_name"]]

        cr_arm_length = curr_point_target["target_size_m"].iloc[0]

        # orientation of boresight in ENU
        elev_bore_enu = np.deg2rad(curr_point_target["corner_elevation_deg"].iloc[0])
        azimuth_bore_enu = np.deg2rad(curr_point_target["corner_azimuth_deg"].iloc[0])

        try:
            sensor_position_at_zd = trajectory.evaluate(row["peak_azimuth_time_[UTC]"])
            cr_position = curr_point_target[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy().squeeze()

            cr_rcs_m2 = _compute_theoretical_rcs_core(
                sensor_position=sensor_position_at_zd,
                target_position=cr_position,
                elev_bore_enu=elev_bore_enu,
                azimuth_bore_enu=azimuth_bore_enu,
                cr_arm_length=cr_arm_length,
                carrier_frequency_hz=carrier_frequency_hz,
            )

            results.append(cr_rcs_m2)
        except TypeError:
            results.append(np.nan)

    return results


def point_target_analysis_with_corrections(
    product_path: str | Path,
    external_target_source: str | Path,
    external_orbit_path: str | Path | None = None,
    config: SCTPointTargetAnalysisConfig | None = None,
) -> tuple[pd.DataFrame, list[PointTargetGraphicalData]]:
    """Point Target Analysis high-level function that executes the proper wrapper of Arepyextras-Quality
    point_target_analysis function based on input product type.

    Parameters
    ----------
    product_path : str | Path
        Path to the input product
    external_target_source : str | Path
        path to external point target source (file or folder)
    external_orbit_path : str | Path | None, optional
        Path to the external orbit file,  by default None
    config : SCTPointTargetAnalysisConfig, optional
        config file SCTPointTargetAnalysisConfig dataclass to enable and manage different features, if provided,
        by default None

    Returns
    -------
    pd.DataFrame
        pandas data frame containing all the computed features for each point target
    list[PointTargetGraphicalData]
        dict of data stored for graphical output needs

    """
    product_path = Path(product_path)
    external_target_source = Path(external_target_source)
    external_orbit_path = Path(external_orbit_path) if external_orbit_path is not None else None
    config = config or SCTPointTargetAnalysisConfig()

    sct_logger.info(f"Input product: {product_path}")
    sct_logger.info(f"Using external target source provided: {external_target_source}")
    if external_orbit_path is not None:
        sct_logger.info(f"Using external orbit {external_orbit_path}")

    if config.enable_etad_corrections:
        config.enable_solid_tides_correction = False
        config.enable_ionospheric_correction = False
        config.enable_tropospheric_correction = False
        config.enable_sensor_specific_processing_corrections = False
        sct_logger.debug("ETAD corrections enabled: forced disabling of other correction")

        if config.etad_product_path is None:
            sct_logger.critical("ETAD corrections requested but the ETAD product path is not valid")
            msg = "Invalid ETAD Product path"
            raise RuntimeError(msg)

    product, rng_corr_func, az_corr_func = product_loader(
        product_path=product_path,
        external_orbit=external_orbit_path,
    )
    first_channel = product.get_channel_data(channel_id=product.channels_list[0])

    point_targets_df = extract_point_target_data_from_source(source=external_target_source)
    nominal_target_coords = point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy()

    if config.enable_solid_tides_correction or config.enable_plate_tectonics_correction:
        update_targets_with_geodynamics_corrections(first_channel, point_targets_df, nominal_target_coords, config)

    results, graph_results = point_target_analysis(
        product=product,
        point_targets=convert_df_to_nominal_point_target(data_df=point_targets_df),
        config=config.base_config,
    )
    if len(results) == 0:
        sct_logger.critical("Point target analysis results is empty: no visible targets detected")
        msg = "No visible point targets"
        raise ValueError(msg)

    results.reset_index(drop=True, inplace=True)
    results.rename(columns={"target": "target_name"}, inplace=True)

    if config.enable_sensor_specific_processing_corrections:
        results = update_results_with_sensor_specific_ale_corrections(
            results,
            product,
            rng_corr_func,
            az_corr_func,
        )

    results["solid_tides_correction"] = config.enable_solid_tides_correction
    results["plate_tectonics_correction"] = config.enable_plate_tectonics_correction

    update_results_with_theoretical_rcs(
        results=results,
        point_targets_df=point_targets_df,
        first_channel=first_channel,
    )

    if config.enable_etad_corrections:
        sct_logger.info("Extracting ALE range corrections from ETAD product...")
        if config.etad_product_path is None:
            msg = "Cannot perform ETAD corrections: missing input etad product"
            raise RuntimeError(msg)
        etad_corrections = get_etad_corrections(etad_product_path=config.etad_product_path, target_df=point_targets_df)
        results = results.merge(etad_corrections, on=["target_name"])

    if config.enable_ionospheric_correction or config.enable_tropospheric_correction:
        results = update_results_with_atmospheric_corrections(
            results=results,
            first_channel=first_channel,
            nominal_target_coords=nominal_target_coords,
            point_targets_df=point_targets_df,
            config=config,
        )

    update_results_with_derived_quantities(results=results)

    sct_logger.info("Analysis completed.")

    return results, graph_results


def update_targets_with_geodynamics_corrections(
    first_channel: ChannelData,
    point_targets_df: pd.DataFrame,
    nominal_target_coords: np.ndarray,
    config: SCTPointTargetAnalysisConfig,
) -> None:
    """Update point target coordinates with geodynamics corrections."""
    # approximating acquisition time with first value of azimuth axis
    acquisition_time = first_channel.azimuth_axis[0]

    coords_displacements = run_compute_geodynamics_corrections(
        nominal_target_coords=nominal_target_coords,
        acquisition_time=acquisition_time,
        point_targets_df=point_targets_df,
        enable_plate_tectonics_correction=config.enable_plate_tectonics_correction,
        enable_solid_tides_correction=config.enable_solid_tides_correction,
    )

    assert coords_displacements is not None
    point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = nominal_target_coords + coords_displacements


def update_results_with_sensor_specific_ale_corrections(
    results: pd.DataFrame,
    product: SCTInputProduct,
    rng_corr_func: ALECorrectionFunctionType | None,
    az_corr_func: ALECorrectionFunctionType | None,
) -> pd.DataFrame:
    """Update results with sensor specific ALE corrections."""
    results["id"] = [uuid4() for _ in range(len(results))]

    range_corrections_df = pd.DataFrame(results["id"].copy(), columns=["id"])
    azimuth_corrections_df = pd.DataFrame(results["id"].copy(), columns=["id"])

    if rng_corr_func is not None:
        sct_logger.info("Computing sensor specific range corrections...")
        range_corrections_df = rng_corr_func(product, results.copy())
    else:
        sct_logger.info("Sensor specific range corrections function has not been selected")

    if az_corr_func is not None:
        sct_logger.info("Computing sensor specific azimuth corrections...")
        azimuth_corrections_df = az_corr_func(product, results.copy())
    else:
        sct_logger.info("Sensor specific azimuth corrections function has not been selected")

    results = results.merge(range_corrections_df, on="id").merge(azimuth_corrections_df, on="id")
    results.drop(columns="id", axis=1, inplace=True)

    return results


def update_results_with_derived_quantities(results: pd.DataFrame) -> None:
    """Update results with derived quantities."""
    results["total_doppler_frequency_[Hz]"] = (
        results["doppler_frequency_[Hz]"] + results["steering_doppler_frequency_[Hz]"]
    )

    # sum all corrections along a specific direction
    results["total_ale_range_correction_[m]"] = results[
        [c for c in results.columns if "_range_correction_[m]" in c]
    ].sum(axis=1)
    results["total_ale_azimuth_correction_[m]"] = results[
        [c for c in results.columns if "_azimuth_correction_[m]" in c]
    ].sum(axis=1)

    # compute corrected ALE measurement
    results["revised_ale_range_[m]"] = (
        results["slant_range_localization_error_[m]"] + results["total_ale_range_correction_[m]"]
    )
    results["revised_ale_azimuth_[m]"] = (
        results["azimuth_localization_error_[m]"] + results["total_ale_azimuth_correction_[m]"]
    )


def update_results_with_atmospheric_corrections(
    results: pd.DataFrame,
    first_channel: ChannelData,
    nominal_target_coords: np.ndarray,
    point_targets_df: pd.DataFrame,
    config: SCTPointTargetAnalysisConfig,
) -> pd.DataFrame:
    """Update results with atmospheric corrections."""
    acquisition_info = AtmosphericDelaysAcquisitionInfo(
        trajectory=first_channel.trajectory,
        azimuth_time=first_channel.mid_azimuth_time,
        carrier_frequency=first_channel.carrier_frequency,
    )
    atmospheric_delays = run_compute_atmospheric_delays(
        target_coords=nominal_target_coords,
        acquisition_info=acquisition_info,
        config=config,
    )
    atmospheric_delays_df = convert_atmospheric_delays_to_df(
        target_names=point_targets_df["target_name"].copy(),
        delays=atmospheric_delays,
    )

    return results.merge(atmospheric_delays_df, on=["target_name"])


def update_results_with_theoretical_rcs(
    results: pd.DataFrame,
    point_targets_df: pd.DataFrame,
    first_channel: ChannelData,
) -> None:
    """Update results with theoretical RCS."""
    theoretical_rcs_information_is_available = all(
        x in point_targets_df for x in ["target_size_m", "corner_elevation_deg", "corner_azimuth_deg"]
    )
    theoretical_rcs = None
    if theoretical_rcs_information_is_available:
        sct_logger.info("Computing theoretical RCS...")
        theoretical_rcs = _compute_theoretical_rcs(
            data_df=results.copy(),
            point_targets_df=point_targets_df.copy(),
            carrier_frequency_hz=first_channel.carrier_frequency,
            trajectory=first_channel.trajectory,
        )

    results["rcs_theoretical_[dB]"] = theoretical_rcs
