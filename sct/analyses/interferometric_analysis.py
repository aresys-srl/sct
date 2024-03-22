# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Interferometric Analysis
------------------------
"""

from __future__ import annotations

import logging
from pathlib import Path

from arepyextras.quality.interferometric_analysis.analysis import interferometric_analysis
from arepyextras.quality.interferometric_analysis.custom_dataclasses import InterferometricCoherenceOutput

from sct.configuration.sct_configuration import SCTInterferometricAnalysisConfig
from sct.io.io_manager import product_loader

# syncing with logger
log = logging.getLogger("quality_analysis")


def interferometric_coherence_analysis(
    product_path: str | Path, config: SCTInterferometricAnalysisConfig | None = None
) -> list[InterferometricCoherenceOutput]:
    """Computing the interferometric analysis of the input product. Product can contain interferogram information or
    coherence information. In the first case, coherence is computed before generating the 2D azimuth and range coherence
    intensity histograms.

    Parameters
    ----------
    product_path : str | Path
        path to the product to be analyzed
    config : SCTInterferometricAnalysisConfig | None, optional
        SCTInterferometricAnalysisConfig configuration dataclass, by default None

    Returns
    -------
    list[InterferometricCoherenceOutput]
        an InterferometricCoherenceOutput dataclass for each channel
    """
    if config is None:
        config = SCTInterferometricAnalysisConfig()

    return sct_interferometric_coherence_analysis(product_path=Path(product_path), config=config)


def sct_interferometric_coherence_analysis(
    product_path: Path, config: SCTInterferometricAnalysisConfig
) -> list[InterferometricCoherenceOutput]:
    """Core computation of coherence and coherence histograms is done using interferometric_analysis arepyextras
    function by passing a proper protocol compliant object from the input product path.

    Parameters
    ----------
    product_path : Path
        path to the product to be analyzed
    config : SCTInterferometricAnalysisConfig
        SCTInterferometricAnalysisConfig configuration dataclass

    Returns
    -------
    list[InterferometricCoherenceOutput]
        an InterferometricCoherenceOutput dataclass for each channel
    """
    # LOADING PRODUCT
    product, _, _ = product_loader(product_path=product_path)

    return interferometric_analysis(product=product, config=config.base_config)
