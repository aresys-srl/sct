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

# custom correction function type to be matched
ALECorrectionFunctionType = Callable[[QualityInputProduct, pd.DataFrame], pd.DataFrame]
