# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Point Target Analysis"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from perseo_quality.point_targets_analysis.analysis import point_target_analysis

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.analyses.point_target.core.utilities import (
    PTA_SCT_ADDITIONAL_OUTPUT_FIELDS,
    update_df_with_llh,
    update_results_with_ale_corrections,
    update_results_with_atmospheric_corrections,
    update_results_with_derived_quantities,
    update_results_with_theoretical_rcs,
    update_targets_with_geodynamics_corrections,
)
from sct.configuration.logger import sct_logger
from sct.io.io_manager import InvalidProductType, product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source

if TYPE_CHECKING:
    from perseo_quality.point_targets_analysis.custom_dataclasses import PointTargetGraphicalData


def sct_point_target_analysis_with_corrections(
    product_path: str | Path,
    external_target_source: str | Path,
    external_orbit_path: str | Path | None = None,
    external_corrections_product: str | Path | None = None,
    config: SCTPointTargetAnalysisConfig | None = None,
) -> tuple[pd.DataFrame, list[PointTargetGraphicalData]]:
    """Point Target Analysis high-level function that executes the proper wrapper of PERSEO-Quality
    point_target_analysis function based on input product type.

    Parameters
    ----------
    product_path : str | Path
        Path to the input product
    external_target_source : str | Path
        path to external point target source (file or folder)
    external_orbit_path : str | Path | None, optional
        Path to the external orbit file, by default None
    external_corrections_product : str | Path | None, optional
        Path to the external ALE corrections product, by default None
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

    if external_corrections_product is not None:
        sct_logger.info(f"Using external corrections product: {external_corrections_product}")

    try:
        product, ale_corrector = product_loader(
            product_path=product_path,
            external_orbit=external_orbit_path,
            external_corrections_product=external_corrections_product,
        )
        first_channel = product.get_channel_data(channel_id=product.channels_list[0])
    except InvalidProductType as err:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        raise InvalidProductType from err

    if ale_corrector is not None:
        config.corrections = ale_corrector.update_corrections_config(config.corrections)

    point_targets_df = extract_point_target_data_from_source(source=external_target_source)
    nominal_target_coords = point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy()

    if config.corrections.enable_solid_tides_correction or config.corrections.enable_plate_tectonics_correction:
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

    results[PTA_SCT_ADDITIONAL_OUTPUT_FIELDS["total_doppler"]] = (
        results["doppler_frequency_[Hz]"] + results["steering_doppler_frequency_[Hz]"]
    )

    results[PTA_SCT_ADDITIONAL_OUTPUT_FIELDS["solid_tides"]] = config.corrections.enable_solid_tides_correction
    results[PTA_SCT_ADDITIONAL_OUTPUT_FIELDS["plate_tectonics"]] = config.corrections.enable_plate_tectonics_correction

    results = update_df_with_llh(results=results, point_targets_df=point_targets_df)

    results = update_results_with_ale_corrections(results=results, product=product, ale_corrector=ale_corrector)

    update_results_with_theoretical_rcs(
        results=results,
        point_targets_df=point_targets_df,
        first_channel=first_channel,
    )

    if config.corrections.enable_ionospheric_correction or config.corrections.enable_tropospheric_correction:
        results = update_results_with_atmospheric_corrections(
            results=results,
            first_channel=first_channel,
            nominal_target_coords=nominal_target_coords,
            point_targets_df=point_targets_df,
            config=config,
        )

    results = update_results_with_derived_quantities(results=results)

    sct_logger.info("Analysis completed.")

    return results, graph_results
