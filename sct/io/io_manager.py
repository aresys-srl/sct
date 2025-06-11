# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O utilities
-------------
"""

from __future__ import annotations

import logging
from enum import Enum, auto
from pathlib import Path
from typing import Union

from arepyextras.eo_products.eos.l1_products.utilities import is_eos04_product
from arepyextras.eo_products.asar.l1_products.utilities import is_asar_product
from arepyextras.eo_products.iceye.l1_products.utilities import is_iceye_product
from arepyextras.eo_products.novasar.l1_products.utilities import is_novasar_1_product
from arepyextras.eo_products.safe.l1_products.utilities import is_s1_safe_product
from arepyextras.eo_products.saocom.l1_products.utilities import is_saocom_product
from arepyextras.quality.io.quality_input_from_product_folder import ProductFolderManager
from arepytools.io.productfolder2 import is_product_folder as is_aresys_product

from sct.core.custom_corrections import ALECorrectionFunctionType, sentinel_1_ipf
from sct.io.extended_protocols import SCTInputProduct
from sct.io.quality_input_from_eos04_product import EOS04ProductManager
from sct.io.quality_input_from_asar_product import ASARProductManager
from sct.io.quality_input_from_iceye_product import ICEYEProductManager
from sct.io.quality_input_from_novasar1_product import NovaSAR1ProductManager
from sct.io.quality_input_from_saocom_product import SAOCOMProductManager
from sct.io.quality_input_from_sentinel1_product import Sentinel1ProductManager

# syncing with logger
log = logging.getLogger("quality_analysis")


class InvalidProductType(RuntimeError):
    """Invalid input product type"""


class SupportedInputProductType(Enum):
    """Supported input product types enum"""

    ARESYS = auto()
    S1_SAFE = auto()
    NOVASAR1 = auto()
    ICEYE = auto()
    SAOCOM = auto()
    EOS04 = auto()
    ASAR = auto()
    UNKNOWN = auto()


def input_detector(product: Union[str, Path]) -> SupportedInputProductType:
    """Detecting the input product type to switch between following processing steps.

    Parameters
    ----------
    product : Union[str, Path]
        Path to the product

    Returns
    -------
    SupportedInputProductType
        detected type for input product
    """

    product = Path(product)

    if is_aresys_product(product):
        return SupportedInputProductType.ARESYS

    if is_s1_safe_product(product):
        return SupportedInputProductType.S1_SAFE

    if is_novasar_1_product(product):
        return SupportedInputProductType.NOVASAR1

    if is_iceye_product(product):
        return SupportedInputProductType.ICEYE

    if is_saocom_product(product):
        return SupportedInputProductType.SAOCOM

    if is_eos04_product(product):
        return SupportedInputProductType.EOS04

    if is_asar_product(product):
        return SupportedInputProductType.ASAR

    return SupportedInputProductType.UNKNOWN


def select_custom_corrections(
    product_type: SupportedInputProductType,
) -> tuple[ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]:
    """Selecting the proper correction functions based on input product type.

    Parameters
    ----------
    product_type : SupportedInputProductType
        product type

    Returns
    -------
    tuple[ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]
        range custom correction function,
        azimuth custom correction function
    """
    if product_type == SupportedInputProductType.S1_SAFE:
        return sentinel_1_ipf.compute_range_corrections, sentinel_1_ipf.compute_azimuth_corrections

    return None, None


def product_loader(
    product_path: Path, external_orbit: Path | None = None
) -> tuple[SCTInputProduct, ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]:
    """Loading product by it type. Extracting a SCTInputProduct protocol-compliant object.

    Parameters
    ----------
    product_path : Path
        Path to the product to be loaded
    external_orbit : Path | None, optional
        Path to external orbit file, if needed, by default None

    Returns
    -------
    tuple[SCTInputProduct, ALECorrectionFunctionType | None, ALECorrectionFunctionType | None]
        SCTInputProduct compliant object,
        range ale correction function or none
        azimuth ale correction function or none
    """
    # DETECTING INPUT PRODUCT TYPE
    input_type = input_detector(product=product_path)

    match input_type:
        case SupportedInputProductType.ARESYS:
            log.info("Product type: Product Folder Aresys")
            product = ProductFolderManager(product_path)
        case SupportedInputProductType.S1_SAFE:
            log.info("Product type: Sentinel-1 SAFE")
            product = Sentinel1ProductManager(product_path, external_orbit_path=external_orbit)
        case SupportedInputProductType.NOVASAR1:
            log.info("Product type: NovaSAR-1")
            product = NovaSAR1ProductManager(product_path)
        case SupportedInputProductType.ICEYE:
            log.info("Product type: ICEYE")
            product = ICEYEProductManager(product_path)
        case SupportedInputProductType.SAOCOM:
            log.info("Product type: SAOCOM")
            product = SAOCOMProductManager(product_path)
        case SupportedInputProductType.EOS04:
            log.info("Product type: EOS-04")
            product = EOS04ProductManager(product_path)
        case SupportedInputProductType.ASAR:
            log.info("Product type: ENVISAT/ERS")
            product = ASARProductManager(product_path)
        case _:
            raise InvalidProductType("Unknown product type")

    # CHOOSING RIGHT CORRECTION FUNCTIONS BASED ON PRODUCT TYPE
    rng_corr_func, az_corr_func = select_custom_corrections(product_type=input_type)
    return product, rng_corr_func, az_corr_func
