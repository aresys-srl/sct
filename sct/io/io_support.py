# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
I/O support utilities
---------------------
"""

import re


class ChannelDataPairMismatch(RuntimeError):
    """Mismatch between channel data pair (raster data and corresponding metadata)"""


class InvalidChannelId(RuntimeError):
    """Invalid channel number"""


# camel case pattern
_cc_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def convert_camel2snake(text: str) -> str:
    """CamelCase to snake_case converter.

    Parameters
    ----------
    text : str
        CamelCase text

    Returns
    -------
    str
        snake_case text
    """
    return _cc_pattern.sub("_", text).lower()
