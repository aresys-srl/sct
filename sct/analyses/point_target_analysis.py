# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target Analysis
---------------------
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
from arepyextras.quality.io.quality_input_protocol import QualityInputProduct, TwiceDifferentiable3DCurve
from arepyextras.quality.point_targets_analysis.analysis import point_target_analysis
from arepyextras.quality.point_targets_analysis.custom_dataclasses import PointTargetGraphicalData
from arepytools.io.io_support import NominalPointTarget
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_default_configuration import SCTPointTargetAnalysisConfig
from sct.core import custom_corrections
from sct.core.custom_corrections import select_custom_corrections
from sct.core.global_corrections import (
    IonosphericInput,
    TroposphereInput,
    compute_atmospheric_delays,
    compute_geodynamics_corrections,
    convert_atmospheric_delays_to_df,
    get_etad_corrections,
)
from sct.io.io_manager import input_detector, product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source

# syncing with logger
log = logging.getLogger("quality_analysis")


@dataclass
class AtmosphericDelaysAcquisitionInfo:
    """Acquisition information required for computing atmospheric delays"""

    trajectory: TwiceDifferentiable3DCurve
    azimuth_time: PreciseDateTime
    carrier_frequency: float


def run_compute_atmospheric_delays(
    target_coords: np.ndarray,
    acquisition_info: AtmosphericDelaysAcquisitionInfo,
    config: SCTPointTargetAnalysisConfig,
) -> tuple[np.ndarray | None, tuple[np.ndarray, np.ndarray] | None]:
    """Compute atmospheric delays"""
    if config.enable_ionospheric_correction and config.ionospheric_maps_directory is None:
        log.critical("Ionospheric perturbation computation requested but the maps directory is not valid")
        raise RuntimeError("Invalid ionospheric maps directory")

    if config.enable_tropospheric_correction and config.tropospheric_maps_directory is None:
        log.critical("Tropospheric perturbation computation requested but the maps directory is not valid")
        raise RuntimeError("Invalid tropospheric maps directory")

    ionosphere_input = None
    if config.enable_ionospheric_correction:
        assert config.ionospheric_analysis_center is not None
        assert config.ionospheric_maps_directory is not None
        ionosphere_input = IonosphericInput(
            analysis_center=config.ionospheric_analysis_center,
            incidence_angle_method=config.ionospheric_tec_inc_angle_method,
            map_dir=config.ionospheric_maps_directory,
        )

    troposphere_input = None
    if config.enable_tropospheric_correction:
        assert config.tropospheric_maps_directory
        assert config.tropospheric_map_grid_resolution
        troposphere_input = TroposphereInput(
            maps_directory=config.tropospheric_maps_directory, maps_resolution=config.tropospheric_map_grid_resolution
        )

    # atmospheric delays for each point target
    return compute_atmospheric_delays(
        target_coords=target_coords,
        trajectory=acquisition_info.trajectory,
        az_time=acquisition_info.azimuth_time,
        fc_hz=acquisition_info.carrier_frequency,
        ionosphere_input=ionosphere_input,
        troposphere_input=troposphere_input,
    )


def main(
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
    tuple[pd.DataFrame, list[PointTargetGraphicalData]]
        pandas data frame containing all the computed features for each point target,
        dict of data stored for graphical output needs
    """

    # Input parameters analysis
    product_path = Path(product_path)
    log.info(f"Input product: {product_path}")

    external_target_source = Path(external_target_source)
    log.info(f"Using external target source provided: {external_target_source}")

    external_orbit_path = Path(external_orbit_path) if external_orbit_path is not None else None
    if external_orbit_path is not None:
        log.info(f"Using external orbit {external_orbit_path}")

    config = config or SCTPointTargetAnalysisConfig()

    # ETAD configuration update
    if config.enable_etad_corrections:
        config.enable_solid_tides_correction = False
        config.enable_ionospheric_correction = False
        config.enable_tropospheric_correction = False
        config.enable_sensor_specific_processing_corrections = False
        log.debug("ETAD corrections enabled: forced disabling of other correction")

        if config.etad_product_path is None:
            log.critical("ETAD corrections requested but the ETAD product path is not valid")
            raise RuntimeError("Invalid ETAD Product path")

    # DETECTING INPUT PRODUCT TYPE
    input_type = input_detector(product=product_path)

    # LOADING PRODUCT
    product, first_channel = product_loader(
        product_path=product_path, external_orbit=external_orbit_path, input_type=input_type
    )
    # CHOOSING RIGHT CORRECTION FUNCTIONS BASED ON PRODUCT TYPE
    rng_corr_func, az_corr_func = select_custom_corrections(product_type=input_type)

    # EXTRACTING PRODUCT ACQUISITION TIME
    acquisition_time = first_channel.azimuth_axis[0]  # approximating acquisition time with firs value of azimuth axis

    # external target source
    point_targets_df = extract_point_target_data_from_source(source=external_target_source)
    nominal_target_coords = point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy()

    # checking if acquisition time lies within point target data time validity boundaries
    try:

        def _to_pdt(date) -> PreciseDateTime:
            return PreciseDateTime.fromisoformat(date.mode()[0].isoformat())

        date_lower_boundary = _to_pdt(point_targets_df["validity_start_date"])
        date_upper_boundary = _to_pdt(point_targets_df["validity_end_date"])

        if not date_lower_boundary <= acquisition_time <= date_upper_boundary:
            raise RuntimeError(
                f"Acquisition time {acquisition_time} date is "
                + f"outside of validity boundaries: [{date_lower_boundary},{date_upper_boundary}]"
            )

        # computing time delta between acquisition time and calibration site measurement campaign date
        time_delta_s = acquisition_time - _to_pdt(point_targets_df["measurement_date"])

    except KeyError as err:
        time_delta_s = 0
        if config.enable_plate_tectonics_correction:
            log.critical("Missing time validity required information in input point targets")
            raise RuntimeError(
                "Cannot apply Plate Tectonics correction: disable this feature from configuration or "
                + "add validity dates to point targets data"
            ) from err

    # COMPUTING GEODYNAMICS CORRECTIONS
    drift_vel = ["drift_velocity_x_my", "drift_velocity_y_my", "drift_velocity_z_my"]
    drift_velocities = None
    if set(drift_vel).issubset(point_targets_df.columns):
        drift_velocities = point_targets_df[drift_vel].to_numpy()

    coords_displacements = compute_geodynamics_corrections(
        target_coords=nominal_target_coords,
        drift_velocities=drift_velocities,
        acq_time=acquisition_time,
        time_delta_s=time_delta_s,
        plate_ref=point_targets_df.plate[0],
        tides_flag=config.enable_solid_tides_correction,
        tectonics_flag=config.enable_plate_tectonics_correction,
    )

    # APPLYING GEODYNAMICS CORRECTIONS TO TARGET COORDINATES
    if coords_displacements is not None:
        point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = nominal_target_coords + coords_displacements

    # converting point target data frame in list of NominalPointTarget dataclasses
    point_targets_data = convert_df_to_nominal_point_target(data_df=point_targets_df)

    # computing atmospheric delays
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
        target_names=point_targets_df["target_name"].copy(), delays=atmospheric_delays
    )

    # computing point target analysis
    data_df, graph_data = sct_point_target_analysis(
        product=product,
        config=config,
        point_targets_data=point_targets_data,
        azimuth_corrections_func=az_corr_func,
        range_corrections_func=rng_corr_func,
    )

    # retrieving ETAD corrections
    if config.enable_etad_corrections:
        log.info("Extracting ALE range corrections from ETAD product...")
        assert config.etad_product_path is not None
        etad_corrections = get_etad_corrections(etad_product_path=config.etad_product_path, target_df=point_targets_df)
        data_df = data_df.merge(etad_corrections, on=["target_name"])

    if config.enable_ionospheric_correction or config.enable_tropospheric_correction:
        data_df = data_df.merge(atmospheric_delays_df, on=["target_name"])

    # sum all corrections along a specific direction
    data_df["total_ale_range_correction_[m]"] = data_df[
        [c for c in data_df.columns if "_range_correction_[m]" in c]
    ].sum(axis=1)
    data_df["total_ale_azimuth_correction_[m]"] = data_df[
        [c for c in data_df.columns if "_azimuth_correction_[m]" in c]
    ].sum(axis=1)

    # compute corrected ALE measurement
    data_df["revised_ale_range_[m]"] = (
        data_df["slant_range_localization_error_[m]"] + data_df["total_ale_range_correction_[m]"]
    )
    data_df["revised_ale_azimuth_[m]"] = (
        data_df["azimuth_localization_error_[m]"] + data_df["total_ale_azimuth_correction_[m]"]
    )

    log.info("Analysis completed.")

    return data_df, graph_data


def sct_point_target_analysis(
    product: QualityInputProduct,
    point_targets_data: dict[str, NominalPointTarget],
    config: SCTPointTargetAnalysisConfig,
    azimuth_corrections_func: custom_corrections.ALECorrectionFunctionType | None = None,
    range_corrections_func: custom_corrections.ALECorrectionFunctionType | None = None,
) -> tuple[pd.DataFrame, list[PointTargetGraphicalData]]:
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
    tuple[pd.DataFrame, list[PointTargetGraphicalData]]
        results dataframe,
        graphs data
    """
    data, graph_data = point_target_analysis(
        product=product,
        point_targets=point_targets_data,
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
        else:
            log.info("Sensor specific range corrections function has not been selected")
        if azimuth_corrections_func is not None:
            log.info("Computing sensor specific azimuth corrections...")
            azimuth_corrections_df = azimuth_corrections_func(product, data.copy())
        else:
            log.info("Sensor specific azimuth corrections function has not been selected")

    # ADDING CORRECTIONS TO RESULTS
    data["solid_tides_correction"] = config.enable_solid_tides_correction
    data["plate_tectonics_correction"] = config.enable_plate_tectonics_correction
    data_out = data.merge(range_corrections_df, on="id").merge(azimuth_corrections_df, on="id")
    data_out.drop(columns="id", axis=1, inplace=True)

    return data_out, graph_data
