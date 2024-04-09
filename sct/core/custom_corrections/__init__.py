# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: Custom Corrections module
------------------------------
"""
from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from sct.io.extended_protocols import SCTInputProduct

# custom correction function type to be matched
ALECorrectionFunctionType = Callable[[SCTInputProduct, pd.DataFrame], pd.DataFrame]
