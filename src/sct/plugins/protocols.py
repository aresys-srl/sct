# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Input Products plugins protocols
--------------------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Protocol, runtime_checkable

from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct

Detector = Callable[[str | Path], bool]

if TYPE_CHECKING:
    # TODO: this is very strange, it must be fixed
    from sct.analyses.point_target.config import SCTPointTargetAnalysisCorrectionsConf


@runtime_checkable
class AbsoluteLocalizationErrorCorrector(Protocol):
    """SCT protocol to define the behavior of specific sensors Absolute Localization Error computation"""

    def __init__(self, external_product_path: Path | None):
        super().__init__()

    def get_ale_corrections_function(self) -> ALECorrectionFunctionType:
        """Getter of the ALE correction function to effectively compute corrections"""

    # TODO: remove this and enforce the behavior in the main code
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

    version: str

    @classmethod
    def get_manager(cls) -> type[SCTInputProduct]:
        """Retrieve manager"""

    @classmethod
    def get_detector(cls) -> Detector:
        """Retrieve detector"""

    @classmethod
    def get_ale_corrector(cls) -> AbsoluteLocalizationErrorCorrector | None:
        """Retrieve ALE corrector class for both range and azimuth directions"""
