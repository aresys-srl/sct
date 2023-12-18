# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Noise Equivalent Sigma Zero (NESZ) Analysis
-------------------------------------------
"""

from pathlib import Path
from typing import Union

from arepyextras.quality.nesz_analysis.analysis import nesz_analysis
from arepyextras.quality.nesz_analysis.custom_dataclasses import NESZOutput

from sct.configuration.sct_default_configuration import (
    SCTNoiseEquivalentSigmaZeroConfig,
)
from sct.io.io_manager import input_detector, product_loader


def main(
    product_path: Union[str, Path],
    external_orbit_path: Union[str, Path] | None = None,
    config: SCTNoiseEquivalentSigmaZeroConfig | None = None,
) -> list[NESZOutput]:
    """Performing Noise Equivalent Sigma-Zero analysis.

    Parameters
    ----------
    product_path : Union[str, Path]
        Path to the product folder
    external_orbit_path : Union[str, Path] | None, optional
        Path to the external orbit file, by default None
    config : SCTNoiseEquivalentSigmaZeroConfig | None, optional
        SCT nesz configuration, by default None

    Returns
    -------
    list[NESZOutput]
        NESZ results, one for each channel
    """
    product_path = Path(product_path)
    external_orbit_path = Path(external_orbit_path) if external_orbit_path is not None else None

    # CONFIGURATION MANAGEMENT
    if config is None:
        # initializing a default configuration
        config = SCTNoiseEquivalentSigmaZeroConfig()

    # DETECTING INPUT PRODUCT TYPE
    input_type = input_detector(product=product_path)

    # LOADING PRODUCT
    product, _ = product_loader(product_path=product_path, external_orbit=external_orbit_path, input_type=input_type)

    return nesz_analysis(product=product, config=config.base_config)
