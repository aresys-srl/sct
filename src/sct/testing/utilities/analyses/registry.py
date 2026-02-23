# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Supported Analyses Registry definition"""

from __future__ import annotations

from sct.testing.utilities.analyses.base import AnalysisHandler
from sct.testing.utilities.common import SCTAnalyses

ANALYSIS_REGISTRY: dict[SCTAnalyses, AnalysisHandler] = {}


def register_analysis(analysis_type: SCTAnalyses, handler: AnalysisHandler):
    """Registration function for AnalysisHandler."""
    ANALYSIS_REGISTRY[analysis_type] = handler
