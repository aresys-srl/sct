# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Input product loading plugins
-----------------------------
"""

from __future__ import annotations

import logging
from functools import partial
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from sct.core.custom_corrections import ALECorrectionFunctionType
from sct.io import (
    quality_input_from_aresys_product,
    quality_input_from_cosmo_product,
    quality_input_from_eos04_product,
    quality_input_from_iceye_product,
    quality_input_from_novasar1_product,
    quality_input_from_radarsat2_product,
    quality_input_from_saocom_product,
    quality_input_from_sentinel1_product,
)
from sct.io.extended_protocols import SCTInputProduct
from sct.io.plugins_utils import get_list_of_valid_plugins, import_plugins

# syncing with logger
log = logging.getLogger("quality_analysis")

Detector = Callable[[str | Path], bool]


@runtime_checkable
class InputProductPluginProtocol(Protocol):
    """Module/Object protocol"""

    @classmethod
    def get_manager(cls) -> type[SCTInputProduct]:
        """Retrieve manager"""

    @classmethod
    def get_detector(cls) -> Detector:
        """Retrieve detector"""

    @classmethod
    def get_azimuth_corrections(cls) -> ALECorrectionFunctionType | None:
        """Retrieve ALE     correction function for azimuth direction"""

    @classmethod
    def get_range_corrections(cls) -> ALECorrectionFunctionType | None:
        """Retrieve ALE correction function for range direction"""


# Built-in input products plugins
INPUT_PRODUCTS_BUILT_IN_PLUGINS = [
    quality_input_from_aresys_product,
    quality_input_from_cosmo_product,
    quality_input_from_eos04_product,
    quality_input_from_iceye_product,
    quality_input_from_novasar1_product,
    quality_input_from_radarsat2_product,
    quality_input_from_saocom_product,
    quality_input_from_sentinel1_product,
]

INPUT_PRODUCTS_BUILT_IN_PLUGINS = get_list_of_valid_plugins(INPUT_PRODUCTS_BUILT_IN_PLUGINS, InputProductPluginProtocol)

import_input_product_plugins = partial(
    import_plugins, plugin_protocol=InputProductPluginProtocol, built_in_plugins=INPUT_PRODUCTS_BUILT_IN_PLUGINS
)
