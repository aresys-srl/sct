# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O utilities
-------------
"""

from __future__ import annotations

import logging
import re
from enum import Enum, auto
from pathlib import Path
from typing import Union

from arepyextras.eo_products.iceye.l1_products.reader import open_product as open_iceye_product
from arepyextras.eo_products.iceye.l1_products.utilities import is_iceye_product
from arepyextras.eo_products.novasar.l1_products.reader import open_product as open_novasar1_product
from arepyextras.eo_products.novasar.l1_products.utilities import is_novasar_1_product
from arepyextras.eo_products.safe.l1_products.reader import open_product as open_s1_product
from arepyextras.eo_products.safe.l1_products.utilities import is_s1_safe_product
from arepyextras.eo_products.saocom.l1_products.reader import open_product as open_saocom_product
from arepyextras.eo_products.saocom.l1_products.utilities import is_saocom_product
from arepyextras.quality.io.quality_input_from_product_folder import ProductFolderManager
from arepyextras.quality.io.quality_input_protocol import ChannelData, QualityInputProduct
from arepytools.io import open_product_folder
from arepytools.io.productfolder2 import is_product_folder as is_aresys_product
from arepytools.timing.precisedatetime import PreciseDateTime

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
    UNKNOWN = auto()


# class SupportedProcessors(Enum):
#     """Supported processors"""


# class SupportedMissions(Enum):
#     """Supported processors"""


# def SCTProductProtocol(QualityInputProduct):

#     def __init__(self) -> None:
#         ...

#     @property
#     def product_type(self) -> SupportedInputProductType:
#         ...

#     @property
#     def mission(self) -> SupportedMissions:
#         ...

#     @property
#     def processor(self) -> SupportedProcessors:
#         ...


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

    return SupportedInputProductType.UNKNOWN


def product_loader(
    product_path: Path, input_type: SupportedInputProductType, external_orbit: Path | None = None
) -> tuple[QualityInputProduct, ChannelData]:
    """Loading product by it type. Extracting a QualityInputProduct protocol-compliant object and the first channel
    ChannelData protocol-compliant object.

    Parameters
    ----------
    product_path : Path
        Path to the product to be loaded
    input_type : SupportedInputProductType
        product type
    external_orbit : Path | None, optional
        Path to external orbit file, if needed, by default None

    Returns
    -------
    tuple[QualityInputProduct, ChannelData]
        QualityInputProduct compliant object,
        first channel ChannelData compliant object
    """
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
        case _:
            raise InvalidProductType("Unknown product type")

    # extracting also first channel
    first_channel = product.get_channel_data(channel_id=product.channels_list[0])

    return product, first_channel


def get_acquisition_time(product: Union[str, Path], product_type: SupportedInputProductType) -> PreciseDateTime:
    """Extract acquisition time from Product.

    Parameters
    ----------
    product : Union[str, Path]
        Path to input product folder
    product_type : SupportedInputProductType
        input product type

    Returns
    -------
    PreciseDateTime
        input product acquisition time
    """
    product = Path(product)

    match product_type:
        case SupportedInputProductType.ARESYS:
            pf = open_product_folder(pf_path=product)
            # taking the first channel metadata
            metadata = pf.get_channel_metadata(channel=pf.get_channels_list()[0])
            acq_time = re.search(
                pattern=r"<AcquisitionStartTime>(.*?)</AcquisitionStartTime>",
                string=metadata.read_text(encoding="utf-8"),
            ).group(1)
            return PreciseDateTime.from_utc_string(acq_time)
        case SupportedInputProductType.S1_SAFE:
            pf = open_s1_product(pf_path=product)
            return pf.acquisition_time
        case SupportedInputProductType.NOVASAR1:
            pf = open_novasar1_product(pf_path=product)
            return pf.acquisition_time
        case SupportedInputProductType.ICEYE:
            pf = open_iceye_product(pf_path=product)
            return pf.acquisition_time
        case SupportedInputProductType.SAOCOM:
            pf = open_saocom_product(pf_path=product)
            return pf.acquisition_time
        case _:
            raise InvalidProductType("Unknown product type")
