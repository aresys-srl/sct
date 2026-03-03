# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Target Ambiguity Ratio Analysis
-------------------------------------
"""

from __future__ import annotations

from sct.analyses.ambiguity_ratio.cli import ptar_analysis
from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig
from sct.analyses.ambiguity_ratio.main import full_pt_ambiguity_ratio_analysis
from sct.core.base import AnalysisHandler
from sct.core.registry import register_analysis

# TODO: match this with config.config_group_name
ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(config=SCTTargetAmbiguityRatioConfig, cli=ptar_analysis, testing=None),
)

__all__ = ["full_pt_ambiguity_ratio_analysis"]
