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

from arepyextras.eo_products.safe.l1_products.reader import open_product
from arepyextras.eo_products.safe.l1_products.utilities import is_s1_safe_product
from arepyextras.quality.io.quality_input_from_product_folder import (
    ProductFolderManager,
)
from arepyextras.quality.io.quality_input_protocol import (
    ChannelData,
    QualityInputProduct,
)
from arepytools.io import open_product_folder
from arepytools.io.productfolder2 import is_product_folder as is_aresys_product
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.io.quality_input_from_safe_product import SafeProductManager

# syncing with logger
log = logging.getLogger("quality_analysis")


class SupportedInputProductType(Enum):
    """Supported input product types enum"""

    ARESYS = auto()
    S1_SAFE = auto()
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
    if input_type == SupportedInputProductType.ARESYS:
        log.info("Product type: Product Folder Aresys")
        product = ProductFolderManager(product_path)
    elif input_type == SupportedInputProductType.S1_SAFE:
        log.info("Product type: Sentinel-1 SAFE")
        product = SafeProductManager(product_path, external_orbit_path=external_orbit)
    else:
        raise RuntimeError("Unknown product type")

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

    if product_type == SupportedInputProductType.ARESYS:
        # reading a channel's raster info to assess the acquisition time
        pf = open_product_folder(pf_path=product)
        # taking the first channel metadata
        metadata = pf.get_channel_metadata(channel=pf.get_channels_list()[0])
        acq_time = re.search(
            pattern=r"<AcquisitionStartTime>(.*?)</AcquisitionStartTime>", string=metadata.read_text(encoding="utf-8")
        ).group(1)

        return PreciseDateTime.from_utc_string(acq_time)

    if product_type == SupportedInputProductType.S1_SAFE:
        pf = open_product(pf_path=product)
        return pf.acquisition_time
