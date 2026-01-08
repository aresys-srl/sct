# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Input product loading plugins
-----------------------------
"""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Callable, Protocol, runtime_checkable

from sct.configuration.point_target_analysis_configuration import SCTPointTargetAnalysisCorrectionsConf
from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct
from sct.io.plugins_framework import import_plugins

Detector = Callable[[str | Path], bool]


@runtime_checkable
class AbsoluteLocalizationErrorCorrector(Protocol):
    """SCT protocol to define the behavior of specific sensors Absolute Localization Error computation"""

    def __init__(self, external_product_path: Path | None):
        super().__init__()

    def get_ale_corrections_function(self) -> ALECorrectionFunctionType:
        """Getter of the ALE correction function to effectively compute corrections"""

    def update_corrections_config(
        self, corrections_config: SCTPointTargetAnalysisCorrectionsConf
    ) -> SCTPointTargetAnalysisCorrectionsConf:
        """Function to update the input SCT Point Target Analysis corrections config to disable specific corrections
        when an external product is provided.

        Parameters
        ----------
        corrections_config : SCTPointTargetAnalysisCorrectionsConf
            SCT Point Target Analysis corrections config to be updated

        Returns
        -------
        SCTPointTargetAnalysisCorrectionsConf
            updated SCT Point Target Analysis corrections config
        """


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
    def get_ale_corrector(cls) -> AbsoluteLocalizationErrorCorrector | None:
        """Retrieve ALE corrector class for both range and azimuth directions"""


import_input_product_plugins = partial(import_plugins, plugin_protocol=InputProductPluginProtocol, plugin_prefix="sct_")
