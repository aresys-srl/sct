# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Point Target Analysis
---------------------------
"""

from __future__ import annotations

from sct.analyses.point_target.cli import target_analysis
from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.analyses.point_target.main import full_point_target_analysis
from sct.analyses.point_target.testing import run_pta_api, run_pta_cli, validate_pta_results
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis

ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(
        config=SCTPointTargetAnalysisConfig,
        cli_command=target_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_pta_api,
            cli_runner=run_pta_cli,
            validator=validate_pta_results,
        ),
    ),
)

__all__ = ["full_point_target_analysis"]
