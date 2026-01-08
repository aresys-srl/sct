# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Elevation Notch Analysis
------------------------
"""

from __future__ import annotations

import sys
from pathlib import Path

from perseo_quality.elevation_notch_analysis.analysis import elevation_notch_analysis
from perseo_quality.elevation_notch_analysis.custom_dataclasses import (
    ElevationNotchOutput,
)

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTElevationNotchAnalysisConfig
from sct.io.antenna_pattern_manager import read_antenna_pattern_netcdf
from sct.io.io_manager import InvalidProductType, product_loader


def sct_elevation_notch_analysis(
    product_path: str | Path,
    antenna_pattern_file: str | Path | None = None,
    config: SCTElevationNotchAnalysisConfig | None = None,
) -> list[ElevationNotchOutput]:
    """Elevation Notch Analysis performed on the input product, taking into account the antenna pattern data, if
    provided.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    antenna_pattern_file : str | Path | None, optional
        path to the antenna pattern NetCDF file, if needed, by default None
    config : SCTElevationNotchAnalysisConfig | None, optional
        configuration parameters, by default None

    Returns
    -------
    list[ElevationNotchOutput]
        list of ElevationNotchOutput analysis output, one for each product channel
    """
    product_path = Path(product_path)
    sct_logger.info(f"Input product: {product_path}")

    config = config or SCTElevationNotchAnalysisConfig()

    # LOADING PRODUCT
    try:
        product, _ = product_loader(
            product_path=product_path,
        )
    except InvalidProductType:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        sys.exit(1)

    # LOADING ANTENNA PATTERN
    antenna_pattern = None
    if antenna_pattern_file is not None:
        sct_logger.info(f"Antenna Pattern provided. Loading data from {antenna_pattern_file}")
        try:
            antenna_pattern = read_antenna_pattern_netcdf(antenna_pattern_file)
        except Exception as err:
            sct_logger.critical("Error while reading antenna pattern file")
            sct_logger.critical(err)
            sys.exit(1)

    return elevation_notch_analysis(
        product=product,
        antenna_pattern=antenna_pattern,
        config=config.base_config,
    )
