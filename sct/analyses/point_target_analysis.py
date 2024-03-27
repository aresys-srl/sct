# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target Analysis
---------------------
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import pandas as pd
from arepyextras.quality.io.quality_input_protocol import QualityInputProduct
from arepyextras.quality.point_targets_analysis.analysis import point_target_analysis
from arepyextras.quality.point_targets_analysis.custom_dataclasses import PointTargetGraphicalData
from arepytools.io.io_support import NominalPointTarget

from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core import custom_corrections
from sct.core.atmospheric_corrections_main import (
    AtmosphericDelaysAcquisitionInfo,
    convert_atmospheric_delays_to_df,
    run_compute_atmospheric_delays,
)
from sct.core.etad_corrections_main import get_etad_corrections
from sct.core.geodynamics_corrections_main import run_compute_geodynamics_corrections
from sct.io.io_manager import product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source

# syncing with logger
log = logging.getLogger("quality_analysis")


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

    # LOADING PRODUCT
    product, rng_corr_func, az_corr_func = product_loader(
        product_path=product_path,
        external_orbit=external_orbit_path,
    )

    # EXTRACTING PRODUCT ACQUISITION TIME
    first_channel = product.get_channel_data(channel_id=product.channels_list[0])
    acquisition_time = first_channel.azimuth_axis[0]  # approximating acquisition time with firs value of azimuth axis

    # external target source
    point_targets_df = extract_point_target_data_from_source(source=external_target_source)
    nominal_target_coords = point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy()

    coords_displacements = run_compute_geodynamics_corrections(
        nominal_target_coords=nominal_target_coords,
        acquisition_time=acquisition_time,
        point_targets_df=point_targets_df,
        config=config,
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
        if config.etad_product_path is None:
            raise RuntimeError("Cannot perform ETAD corrections: missing input etad product")
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
    range_corrections_df = pd.DataFrame(data["id"].copy(), columns=["id"])
    azimuth_corrections_df = pd.DataFrame(data["id"].copy(), columns=["id"])
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
