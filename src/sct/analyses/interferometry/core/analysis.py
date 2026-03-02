# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Interferometric Analysis"""

from __future__ import annotations

from pathlib import Path

from perseo_quality.interferometric_analysis.analysis import interferometric_analysis
from perseo_quality.interferometric_analysis.custom_dataclasses import InterferometricCoherenceOutput

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig
from sct.configuration.logger import sct_logger
from sct.io.io_manager import InvalidProductType, product_loader


def sct_interferometric_coherence_analysis(
    product_path: str | Path,
    second_product_path: str | Path | None = None,
    config: SCTInterferometricAnalysisConfig | None = None,
) -> list[InterferometricCoherenceOutput]:
    """Computing the interferometric analysis of the input product. Product can contain interferogram information or
    coherence information. In the first case, coherence is computed before generating the 2D azimuth and range coherence
    intensity histograms, if enabled in configuration.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed. it must be an interferogram product or a co-registered product but in that
        case a second product must be provided
    second_product_path : str | Path | None, optional
        path to the second co-registered product to be analyzed, by default None
    config : SCTInterferometricAnalysisConfig | None, optional
        SCTInterferometricAnalysisConfig configuration dataclass, by default None

    Returns
    -------
    list[InterferometricCoherenceOutput]
        an InterferometricCoherenceOutput dataclass for each channel
    """
    product_path = Path(product_path)

    if config is None:
        config = SCTInterferometricAnalysisConfig()

    if second_product_path is not None:
        config.base_config.enable_coherence_computation = True

    try:
        product, _ = product_loader(product_path=product_path)
    except InvalidProductType as err:
        sct_logger.critical(f"Unknown product type {product_path}.")
        sct_logger.critical("Please check that the dedicated format plugin is installed.")
        raise InvalidProductType from err

    second_product = None
    if second_product_path is not None:
        second_product_path = Path(second_product_path)
        try:
            second_product, _ = product_loader(product_path=second_product_path)
        except InvalidProductType as err:
            sct_logger.critical(f"Unknown product type {second_product_path}.")
            sct_logger.critical("Please check that the dedicated format plugin is installed.")
            raise InvalidProductType from err

    return interferometric_analysis(product=product, second_product=second_product, config=config.base_config)
