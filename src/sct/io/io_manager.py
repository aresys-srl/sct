# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O utilities
-------------
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sct.configuration.logger import sct_logger
from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct
from sct.io.input_product_plugins import import_input_product_plugins


class InvalidProductType(RuntimeError):
    """Invalid input product type"""


def product_loader(
    product_path: Path,
    external_orbit: Path | None = None,
    external_corrections_product: Path | None = None,
    additional_plugins: list[str] | None = None,
) -> tuple[SCTInputProduct, ALECorrectionFunctionType | None]:
    """Load any supported product

    Parameters
    ----------
    product_path : Path
        Path to the product to be loaded
    external_orbit : Path | None, optional
        Path to external orbit file, if needed, by default None
    external_corrections_product : Path | None, optional
        Path to external ALE corrections product, if needed, by default None
    additional_plugins: list[str] | None, optional
        list of plugins as strings: either absolute paths or importable python modules

    Returns
    -------
    SCTInputProduct
        SCTInputProduct compliant object
    ALECorrectionFunctionType | None
        range and azimuth ale corrections function (if available)
    """
    additional_plugins = additional_plugins or []
    available_plugins = import_input_product_plugins(additional_plugins=additional_plugins)

    product: Optional[SCTInputProduct] = None
    for plugin in available_plugins:
        if plugin.get_detector()(product_path):
            manager = plugin.get_manager()
            ale_corrector = plugin.get_ale_corrector()
            sct_logger.info(f"Using plugin {plugin.__name__}, version {plugin.__version__}")
            sct_logger.info(f"Product type: {manager.__name__}")
            product = manager(product_path, external_orbit_path=external_orbit)
            ale_corr = ale_corrector(external_corrections_product) if ale_corrector is not None else None
            break

    if product is None:
        raise InvalidProductType(f"Unknown input product: {product_path}")

    return product, ale_corr
