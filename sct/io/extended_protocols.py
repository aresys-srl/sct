# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O Extended Protocols
----------------------
"""

from typing import Protocol, runtime_checkable

from arepyextras.quality.io.quality_input_protocol import QualityInputProduct
from shapely import Polygon


@runtime_checkable
class SCTInputProduct(QualityInputProduct, Protocol):
    """SCT extended version of QualityInputProduct protocol"""

    @property
    def footprint(self) -> Polygon | None:
        """Get product scene footprint as a Shapely Polygon"""
