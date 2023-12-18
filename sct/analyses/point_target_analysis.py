# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target Analysis
---------------------
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Union
from uuid import uuid4

import pandas as pd
from arepyextras.quality.io.quality_input_protocol import QualityInputProduct
from arepyextras.quality.point_targets_analysis.analysis import point_target_analysis
from arepytools.io.io_support import NominalPointTarget
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_default_configuration import SCTPointTargetAnalysisConfig
from sct.core import custom_corrections
from sct.core.custom_corrections import select_custom_corrections
from sct.core.global_corrections import (
    compute_atmospheric_delays,
    compute_geodynamics_corrections,
    convert_atmospheric_delays_to_df,
)
from sct.io.io_manager import input_detector, product_loader
from sct.io.point_target_manager import (
    SupportedCalibrationSites,
    convert_df_to_nominal_point_target,
    extract_point_target_data_from_source,
    query_calibration_sites_db,
)

# syncing with logger
log = logging.getLogger("quality_analysis")


def main(
    product_path: Union[str, Path],
    external_orbit_path: Union[str, Path] | None = None,
    calibration_site: Union[str, SupportedCalibrationSites] | None = None,
    external_target_source: Union[str, Path] | None = None,
    config: SCTPointTargetAnalysisConfig | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Point Target Analysis high-level function that executes the proper wrapper of Arepyextras-Quality
    point_target_analysis function based on input product type.

    Parameters
    ----------
    product_path : Union[str, Path]
        Path to the input product
    external_orbit_path : Union[str, Path], optional
        Path to the external orbit file,  by default None
    calibration_site : Union[str, SupportedCalibrationSites], optional
        calibration site to be analyzed, by default None
    external_target_source : Union[str, Path], optional
        path to external point target source (file or folder), by default None
    config : SCTPointTargetAnalysisConfig, optional
        config file SCTPointTargetAnalysisConfig dataclass to enable and manage different features, if provided,
        by default None

    Returns
    -------
    tuple[pd.DataFrame, dict]
        pandas dataframe containing all the computed features for each point target,
        dict of data stored for graphical output needs
    """

    product_path = Path(product_path)
    external_orbit_path = Path(external_orbit_path) if external_orbit_path is not None else None

    # DETECTING INPUT PRODUCT TYPE
    input_type = input_detector(product=product_path)

    # LOADING PRODUCT
    product, first_channel = product_loader(
        product_path=product_path, external_orbit=external_orbit_path, input_type=input_type
    )

    # EXTRACTING PRODUCT ACQUISITION TIME
    acquisition_time = first_channel.azimuth_axis[0]  # approximating acquisition time with firs value of azimuth axis

    # CONFIGURATION MANAGEMENT
    if config is None:
        # initializing a default configuration
        config = SCTPointTargetAnalysisConfig()

    # CALIBRATION SITES MANAGEMENT
    if external_target_source is None:
        # accessing internal database
        if calibration_site is None:
            log.critical(
                "Cannot perform point target analysis: no external file provided and no calibration site selected"
            )
            raise RuntimeError
        log.info(f"Querying calibration sites DB: extracting {calibration_site} info...")
        point_targets_df = query_calibration_sites_db(
            calibration_site=SupportedCalibrationSites(calibration_site), acquisition_time=acquisition_time
        )
    else:
        external_target_source = Path(external_target_source)
        log.info(f"Using external target source provided: {external_target_source}")
        # external target source management
        point_targets_df = extract_point_target_data_from_source(source=external_target_source)

    # checking if acquisition time lies within point target data time validity boundaries
    try:
        date_lower_boundary = PreciseDateTime.fromisoformat(
            point_targets_df["validity_start_date"].mode()[0].isoformat()
        )
        date_upper_boundary = PreciseDateTime.fromisoformat(point_targets_df["validity_end_date"].mode()[0].isoformat())

        if acquisition_time < date_lower_boundary or acquisition_time > date_upper_boundary:
            raise RuntimeError(
                f"Acquisition time {acquisition_time} date is outside of validity boundaries"
                + f"for selected {calibration_site} data"
            )

        # computing time delta between acquisition time and calibration site measurement campaign date
        time_delta_s = acquisition_time - PreciseDateTime.fromisoformat(
            point_targets_df["measurement_date"].mode()[0].isoformat()
        )
    except KeyError as err:
        time_delta_s = 0
        if config.enable_plate_tectonics_correction:
            log.critical("Missing time validity required information in input point targets")
            raise RuntimeError(
                "Cannot apply Plate Tectonics correction: disable this feature from configuration or "
                + "add validity dates to point targets data"
            ) from err

    # COMPUTING GEODYNAMICS CORRECTIONS
    target_coords = point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy()
    drift_vel = ["drift_velocity_x_my", "drift_velocity_y_my", "drift_velocity_z_my"]
    drift_velocities = None
    if set(drift_vel).issubset(point_targets_df.columns):
        drift_velocities = point_targets_df[drift_vel].to_numpy()

    coords_displacements = compute_geodynamics_corrections(
        target_coords=target_coords,
        drift_velocities=drift_velocities,
        acq_time=acquisition_time,
        time_delta_s=time_delta_s,
        plate_ref=point_targets_df.plate[0],
        tides_flag=config.enable_solid_tides_correction,
        tectonics_flag=config.enable_plate_tectonics_correction,
    )

    # APPLYING GEODYNAMICS CORRECTIONS TO TARGET COORDINATES
    if coords_displacements is not None:
        point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = target_coords + coords_displacements

    # converting point target dataframe in list of NominalPointTarget dataclasses
    point_targets_data = convert_df_to_nominal_point_target(data_df=point_targets_df)

    # COMPUTING ATMOSPHERIC CORRECTIONS
    iono_flag = config.enable_ionospheric_correction and config.ionospheric_maps_directory is not None
    tropo_flag = config.enable_tropospheric_correction and config.tropospheric_maps_directory is not None
    # atmospheric delays for each point target
    atmospheric_delays = compute_atmospheric_delays(
        target_coords=target_coords,
        trajectory=first_channel.trajectory,
        az_time=first_channel.mid_azimuth_time,
        fc_hz=first_channel.carrier_frequency,
        analysis_center=config.ionospheric_analysis_center,
        ionosphere_incidence_angle_method=config.ionospheric_tec_inc_angle_method,
        troposphere_map_resolution=config.tropospheric_map_grid_resolution,
        ionosphere_flag=iono_flag,
        ionosphere_map_dir=config.ionospheric_maps_directory,
        troposphere_flag=tropo_flag,
        troposphere_map_dir=config.tropospheric_maps_directory,
    )
    atmospheric_delays_df = convert_atmospheric_delays_to_df(
        target_names=point_targets_df["target_name"].copy(), delays=tuple(atmospheric_delays)
    )

    # CHOOSING RIGHT CORRECTION FUNCTIONS BASED ON PRODUCT TYPE
    rng_corr_func, az_corr_func = select_custom_corrections(product_type=input_type)

    # COMPUTING POINT TARGET ANALYSIS
    data_df, graph_data = sct_point_target_analysis(
        product=product,
        config=config,
        point_targets_data=point_targets_data,
        azimuth_corrections_func=az_corr_func,
        range_corrections_func=rng_corr_func,
    )

    return data_df.merge(atmospheric_delays_df, on=["target_name"]), graph_data


def sct_point_target_analysis(
    product: QualityInputProduct,
    point_targets_data: dict[str, NominalPointTarget],
    config: SCTPointTargetAnalysisConfig,
    azimuth_corrections_func: custom_corrections.ALECorrectionFunctionType | None = None,
    range_corrections_func: custom_corrections.ALECorrectionFunctionType | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Point target analysis wrapper customized for SCT workflow.

    Parameters
    ----------
    product : QualityInputProduct
        product to be analyzed
    point_targets_data : dict[str, NominalPointTarget]
        point target data
    config : SCTPointTargetAnalysisConfig
        analysis configuration
    azimuth_corrections_func : custom_corrections.ALECorrectionFunctionType | None, optional
        function selected for sensor specific azimuth corrections, by default None
    range_corrections_func : custom_corrections.ALECorrectionFunctionType | None, optional
        function selected for sensor specific range corrections, by default None

    Returns
    -------
    tuple[pd.DataFrame, dict]
        results dataframe and graphs data
    """
    data, graph_data = point_target_analysis(
        product=product,
        point_targets=point_targets_data,
        ale_limits=config.ale_validity_limits,
        config=config.base_config,
    )
    data.reset_index(drop=True, inplace=True)
    data.rename(columns={"target": "target_name"}, inplace=True)
    data["total_doppler_frequency_[Hz]"] = data["doppler_frequency_[Hz]"] + data["steering_doppler_frequency_[Hz]"]
    # creating a unique id for each row in the original dataframe
    data["id"] = [uuid4() for _ in range(len(data))]

    # COMPUTING SENSOR SPECIFIC CORRECTIONS
    range_corrections_df = pd.DataFrame([None] * len(data), columns=["total_range_ale_correction_[m]"])
    range_corrections_df["id"] = data["id"].copy()
    azimuth_corrections_df = pd.DataFrame([None] * len(data), columns=["total_azimuth_ale_correction_[m]"])
    azimuth_corrections_df["id"] = data["id"].copy()
    if config.enable_sensor_specific_processing_corrections:
        # ale: slant_range_localization_error and azimuth_localization_error
        # atmospheric corrections
        if range_corrections_func is not None:
            log.info("Computing sensor specific range corrections...")
            range_corrections_df = range_corrections_func(product, data.copy())
            range_corrections_df["total_range_ale_correction_[m]"] = range_corrections_df[
                [c for c in range_corrections_df.columns if "id" not in c]
            ].sum(axis=1)
        else:
            log.info("Sensor specific range corrections function has not been selected")
        if azimuth_corrections_func is not None:
            log.info("Computing sensor specific azimuth corrections...")
            azimuth_corrections_df = azimuth_corrections_func(product, data.copy())
            azimuth_corrections_df["total_azimuth_ale_correction_[m]"] = azimuth_corrections_df[
                [c for c in azimuth_corrections_df.columns if "id" not in c]
            ].sum(axis=1)
        else:
            log.info("Sensor specific azimuth corrections function has not been selected")

    # ADDING CORRECTIONS TO RESULTS
    data_out = data.merge(range_corrections_df, on="id").merge(azimuth_corrections_df, on="id")
    data_out.drop(columns="id", axis=1, inplace=True)

    log.info("Analysis completed.")

    return data_out, graph_data
