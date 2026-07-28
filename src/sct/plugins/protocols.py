# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT plugins protocols (input products and analyses)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Protocol, TypeVar, runtime_checkable

from sct.io.extended_protocols import ALECorrectionFunctionType, SCTInputProduct

if TYPE_CHECKING:
    from typer import Typer

    from sct.core.base import AnalysisHandler

Detector = Callable[[str | Path], bool]

# Generic corrections-config type. The concrete type lives in the analysis plugin
# that owns the point target analysis; core SCT must stay analysis-agnostic, so the
# corrector is parametrized instead of importing a plugin-specific config class.
CorrectionsConfigT = TypeVar("CorrectionsConfigT")


@runtime_checkable
class AbsoluteLocalizationErrorCorrector(Protocol[CorrectionsConfigT]):
    """SCT protocol to define the behavior of specific sensors Absolute Localization Error computation"""

    def __init__(self, external_product_path: Path | None):
        super().__init__()

    def get_ale_corrections_function(self) -> ALECorrectionFunctionType:
        """Getter of the ALE correction function to effectively compute corrections"""

    def update_corrections_config(self, corrections_config: CorrectionsConfigT) -> CorrectionsConfigT:
        """Update the input corrections config to disable specific corrections when an external product is provided.

        Parameters
        ----------
        corrections_config : CorrectionsConfigT
            corrections config to be updated

        Returns
        -------
        CorrectionsConfigT
            updated corrections config
        """


@runtime_checkable
class InputProductPluginProtocol(Protocol):
    """Input product plugin protocol.

    Input product plugins are discovered via the ``sct.input_products``
    entry-point namespace. Each plugin encapsulates the knowledge required to
    read and validate a specific SAR product format, together with an optional
    detector function (to recognize that format from a path) and an optional
    absolute-localization-error corrector.

    The entry-point object must be importable without importing the heavy
    product-access implementation; all heavy imports should be deferred to the
    manager, detector and corrector classes returned by the accessor methods.
    """

    version: str

    @classmethod
    def get_manager(cls) -> type[SCTInputProduct]:
        """Return the input product manager class for this format.

        The manager class implements ``SCTInputProduct`` and provides read
        access to the SAR product data (metadata, raster, auxiliary files).

        Returns
        -------
        type[SCTInputProduct]
            manager class for the product format
        """

    @classmethod
    def get_detector(cls) -> Detector:
        """Return a callable that detects whether a path belongs to this format.

        The detector is a ``Detector`` (``Callable[[str | Path], bool]``) that
        inspects the given path and returns ``True`` if the data matches the
        product format.

        Returns
        -------
        Detector
            detection callable
        """

    @classmethod
    def get_ale_corrector(cls) -> AbsoluteLocalizationErrorCorrector | None:
        """Return the ALE corrector class, or ``None`` if not supported.

        The corrector is used to adjust the absolute localization error
        (range/azimuth biases) that may affect the product.

        Returns
        -------
        AbsoluteLocalizationErrorCorrector | None
            corrector class, or ``None`` if ALE correction is not available
        """


@runtime_checkable
class AnalysisPluginProtocol(Protocol):
    """Analysis plugin protocol.

    Analysis plugins are discovered via the ``sct.analyses`` entry-point namespace.
    The protocol is intentionally input-agnostic: each plugin defines, validates and
    provides its own inputs, configuration, CLI and testing hooks. The entry-point
    object must be importable without importing the heavy analysis implementation
    (``main``/``core``) or the scientific stack.
    """

    version: str
    short_help: str

    @classmethod
    def get_handlers(cls) -> dict[str, AnalysisHandler]:
        """Retrieve the analysis handlers exposed by this plugin.

        A single plugin may expose more than one analysis type (e.g. radiometry
        exposes several types sharing one CLI group).

        Returns
        -------
        dict[str, AnalysisHandler]
            mapping of analysis type name to its handler
        """

    @classmethod
    def get_cli(cls) -> Typer | Callable:
        """Retrieve the plugin CLI (a Typer group or a single command callable)."""
