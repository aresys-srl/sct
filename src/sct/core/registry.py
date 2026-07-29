# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Analyses Registry.

Analyses are discovered lazily through the ``sct.analyses`` entry-point namespace.
Discovery (and therefore importing the heavy analysis implementations) only happens
on first access via `get_analysis_registry` / `load_analyses`, never at
``import sct`` time.
"""

from __future__ import annotations

from sct.core.base import AnalysisHandler

ANALYSIS_REGISTRY: dict[str, AnalysisHandler] = {}

_ANALYSES_LOADED = False


def register_analysis(analysis_type: str, handler: AnalysisHandler) -> None:
    """Registration of an AnalysisHandler."""
    ANALYSIS_REGISTRY[analysis_type] = handler


def load_analyses(*, force: bool = False) -> None:
    """Discover and register all installed analysis plugins (memoized).

    Parameters
    ----------
    force : bool, optional
        re-run discovery even if it already ran, by default False
    """
    global _ANALYSES_LOADED
    if _ANALYSES_LOADED and not force:
        return

    # Imported lazily: the loader pulls in the plugin protocols (and their heavy
    # dependencies), which must not be imported at ``import sct`` time.
    from sct.plugins import get_available_analyses_plugins

    for plugin in get_available_analyses_plugins():
        for analysis_type, handler in plugin.get_handlers().items():
            register_analysis(analysis_type, handler)

    _ANALYSES_LOADED = True


def get_analysis_registry() -> dict[str, AnalysisHandler]:
    """Return the analyses registry, triggering plugin discovery on first use."""
    load_analyses()
    return ANALYSIS_REGISTRY
