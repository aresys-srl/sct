# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O utilities
-------------
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from arepyextras.quality.io.quality_input_protocol import QualityInputProduct

from sct.core.custom_corrections import ALECorrectionFunctionType
from sct.io.input_product_plugins import import_input_product_plugins

# syncing with logger
log = logging.getLogger("quality_analysis")


class InvalidProductType(RuntimeError):
    """Invalid input product type"""


def product_loader(
    product_path: Path, external_orbit: Path | None = None, plugins: list[str] | None = None
) -> tuple[QualityInputProduct, ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]:
    """Load any supported product

    Parameters
    ----------
    product_path : Path
        Path to the product to be loaded
    external_orbit : Path | None, optional
        Path to external orbit file, if needed, by default None
    plugins: list[str] | None, optional
        list of plugins as strings: either absolute paths or importable python modules

    Returns
    -------
    tuple[QualityInputProduct, ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]
        QualityInputProduct compliant object
        range ale correction function (if available)
        azimuth ale correction function (if available)
    """
    plugins = plugins or []
    available_plugins = import_input_product_plugins(plugins)

    product: Optional[QualityInputProduct] = None
    for plugin in available_plugins:
        if plugin.get_detector()(product_path):
            manager = plugin.get_manager()
            log.info(f"Product type: {manager.__name__}")
            product = manager(product_path, external_orbit_path=external_orbit)
            rg_corr: ALECorrectionFunctionType | None = plugin.get_range_corrections()
            az_corr: ALECorrectionFunctionType | None = plugin.get_azimuth_corrections()
            break

    if product is None:
        raise InvalidProductType(f"Unknown input product: {product_path}")

    return product, rg_corr, az_corr
