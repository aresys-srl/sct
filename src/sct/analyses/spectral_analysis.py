# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Spectral Analysis
-----------------
"""

from __future__ import annotations

import sys
from pathlib import Path

from perseo_quality.spectral_analysis.analysis import (
    block_wise_distributed_spectral_analysis,
    point_target_spectral_analysis,
)
from perseo_quality.spectral_analysis.custom_dataclasses import (
    DistributedSpectraDataOutput,
    PointTargetSpectraDataOutput,
)

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTSpectralAnalysisConfig
from sct.io.io_manager import InvalidProductType, product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source


def sct_point_target_spectral_analysis(
    product_path: str | Path, external_target_source: str | Path, config: SCTSpectralAnalysisConfig | None = None
) -> list[PointTargetSpectraDataOutput]:
    """Spectral Analysis performed at each target position for the input product.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    external_target_source : str | Path
        path to external point target source (file or folder)
    config : SCTSpectralAnalysisConfig | None, optional
        configuration parameters, by default None

    Returns
    -------
    list[PointTargetSpectraDataOutput]
        list of PointTargetSpectraDataOutput analysis output, one for each product channel and each Point Target
    """
    product_path = Path(product_path)
    sct_logger.info(f"Input product: {product_path}")

    external_target_source = Path(external_target_source)
    sct_logger.info(f"Using external target source provided: {external_target_source}")

    config = config or SCTSpectralAnalysisConfig()

    # LOADING PRODUCT
    try:
        product, _ = product_loader(
            product_path=product_path,
        )
    except InvalidProductType:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        sys.exit(1)

    # external target source
    point_targets_df = extract_point_target_data_from_source(source=external_target_source)

    # converting point target data frame in list of NominalPointTarget dataclasses
    point_targets_data = convert_df_to_nominal_point_target(data_df=point_targets_df)

    return point_target_spectral_analysis(
        product=product, point_targets=point_targets_data, cropping_size=config.cropping_size
    )


def sct_distributed_spectral_analysis(
    product_path: str | Path,
    config: SCTSpectralAnalysisConfig | None = None,
) -> list[DistributedSpectraDataOutput]:
    """Spectral Analysis performed by partitioning the product in blocks and performing spectral analysis on each of
    them.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    config : SCTSpectralAnalysisConfig | None, optional
        configuration parameters, by default None

    Returns
    -------
    list[DistributedSpectraDataOutput]
        list of DistributedSpectraDataOutput analysis output, one for each product channel and block
    """
    product_path = Path(product_path)
    sct_logger.info(f"Input product: {product_path}")

    config = config or SCTSpectralAnalysisConfig()

    # LOADING PRODUCT
    try:
        product, _ = product_loader(
            product_path=product_path,
        )
    except InvalidProductType:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        sys.exit(1)

    return block_wise_distributed_spectral_analysis(
        product=product,
        azimuth_block_size=config.azimuth_block_size,
    )
