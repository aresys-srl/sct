# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Aresys Product Folder format Arepyextras-Quality protocol-compliant wrapper
---------------------------------------------------------------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from arepyextras.quality.io.quality_input_from_product_folder import ProductFolderManager
from arepytools.io.productfolder2 import is_product_folder as is_aresys_product
from shapely import Polygon


class ProductFolderManagerExtended(ProductFolderManager):
    def __init__(self, path: str | Path, **kwargs) -> None:
        super().__init__(path)

    @property
    def footprint(self) -> Polygon | None:
        """Get product scene footprint as a Shapely Polygon"""
        # TODO: add this property
        ...


def get_manager() -> type[ProductFolderManagerExtended]:
    """Retrieve manager"""
    return ProductFolderManagerExtended


def get_detector() -> Callable[[str | Path], bool]:
    """Retrieve detector"""
    return is_aresys_product


def get_azimuth_corrections():
    """Retrieve ALE correction function for azimuth direction"""
    return None


def get_range_corrections():
    """Retrieve ALE correction function for range direction"""
    return None
