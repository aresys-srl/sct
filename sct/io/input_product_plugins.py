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

from sct import sct_discovered_plugins
from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct
from sct.io.plugins_utils import import_plugins

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


import_input_product_plugins = partial(
    import_plugins, plugin_protocol=InputProductPluginProtocol, built_in_plugins=list(sct_discovered_plugins.values())
)
