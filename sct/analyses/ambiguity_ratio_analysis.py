# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
PTAR Analysis
-------------
"""

from __future__ import annotations

from pathlib import Path

from arepyextras.quality.target_ambiguity_ratio_analysis.analysis import point_target_ambiguity_ratio_analysis
from arepyextras.quality.target_ambiguity_ratio_analysis.custom_dataclasses import AmbiguityRatioOutput

from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTTargetAmbiguityRatioConfig
from sct.io.io_manager import product_loader
from sct.io.point_target_manager import convert_df_to_nominal_point_target, extract_point_target_data_from_source


def sct_point_target_ambiguity_ratio_analysis(
    product_path: str | Path, external_target_source: str | Path, config: SCTTargetAmbiguityRatioConfig | None = None
) -> list[AmbiguityRatioOutput]:
    # Input parameters analysis
    product_path = Path(product_path)
    sct_logger.info(f"Input product: {product_path}")

    external_target_source = Path(external_target_source)
    sct_logger.info(f"Using external target source provided: {external_target_source}")

    config = config or SCTTargetAmbiguityRatioConfig()

    # LOADING PRODUCT
    product, _, _ = product_loader(
        product_path=product_path,
    )

    # external target source
    point_targets_df = extract_point_target_data_from_source(source=external_target_source)

    # converting point target data frame in list of NominalPointTarget dataclasses
    point_targets_data = convert_df_to_nominal_point_target(data_df=point_targets_df)

    return point_target_ambiguity_ratio_analysis(
        product=product, point_targets=point_targets_data, config=config.base_config
    )
