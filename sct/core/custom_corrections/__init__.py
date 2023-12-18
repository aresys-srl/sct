# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: Custom Corrections module
------------------------------
"""
from __future__ import annotations

from collections.abc import Callable

import pandas as pd
from arepyextras.quality.io.quality_input_protocol import QualityInputProduct

from sct.core.custom_corrections import sentinel_1_ipf
from sct.io.io_manager import SupportedInputProductType

# custom correction function type to be matched
ALECorrectionFunctionType = Callable[[QualityInputProduct, pd.DataFrame], pd.DataFrame]


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
    else:
        return None, None
