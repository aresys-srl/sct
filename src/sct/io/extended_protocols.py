# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Input product extended protocol."""

from collections.abc import Callable
from typing import Protocol, runtime_checkable

import pandas as pd
from perseo_quality.io.quality_input_protocol import QualityInputProduct
from shapely import Polygon


@runtime_checkable
class SCTInputProduct(QualityInputProduct, Protocol):
    """SCT extended version of QualityInputProduct protocol"""

    @property
    def footprint(self) -> Polygon | None:
        """Get product scene footprint as a Shapely Polygon"""


# custom correction function type to be matched
ALECorrectionFunctionType = Callable[[SCTInputProduct, pd.DataFrame], pd.DataFrame]
