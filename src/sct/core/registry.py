# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Analyses Registry"""

from __future__ import annotations

from sct.core.base import AnalysisHandler

ANALYSIS_REGISTRY: dict[str, AnalysisHandler] = {}


def register_analysis(analysis_type: str, handler: AnalysisHandler):
    """Registration of an AnalysisHandler."""
    ANALYSIS_REGISTRY[analysis_type] = handler
