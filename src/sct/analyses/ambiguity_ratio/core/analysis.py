# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Target Ambiguity Ratio Analysis"""

from __future__ import annotations

from pathlib import Path

from perseo_quality.tar_analysis.analysis import point_target_ambiguity_ratio_analysis
from perseo_quality.tar_analysis.custom_dataclasses import PointTargetAmbiguityRatioDataOutput

from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig
from sct.configuration.logger import sct_logger
from sct.io.io_manager import InvalidProductType, product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source


def sct_point_target_ambiguity_ratio_analysis(
    product_path: str | Path, external_target_source: str | Path, config: SCTTargetAmbiguityRatioConfig | None = None
) -> list[PointTargetAmbiguityRatioDataOutput]:
    """Point Target Ambiguity Ratio Analysis performed on the input product.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    external_target_source : str | Path
        path to external point target source
    config : SCTTargetAmbiguityRatioConfig | None, optional
        configuration parameters, by default None

    Returns
    -------
    list[PointTargetAmbiguityRatioDataOutput]
        list of PointTargetAmbiguityRatioDataOutput analysis output, one for each product channel and each Point Target
    """
    # Input parameters analysis
    product_path = Path(product_path)
    sct_logger.info(f"Input product: {product_path}")

    external_target_source = Path(external_target_source)
    sct_logger.info(f"Using external target source provided: {external_target_source}")

    config = config or SCTTargetAmbiguityRatioConfig()

    # LOADING PRODUCT
    try:
        product, _ = product_loader(
            product_path=product_path,
        )
    except InvalidProductType as err:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        raise InvalidProductType from err

    # external target source
    point_targets_df = extract_point_target_data_from_source(source=external_target_source)

    # converting point target data frame in list of NominalPointTarget dataclasses
    point_targets_data = convert_df_to_nominal_point_target(data_df=point_targets_df)

    return point_target_ambiguity_ratio_analysis(
        product=product, point_targets=point_targets_data, config=config.base_config
    )
