# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Elevation Notch Analysis
------------------------------
"""

from __future__ import annotations

from sct.analyses.elevation_notch.cli import notch_analysis
from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig
from sct.analyses.elevation_notch.main import full_elevation_notch_analysis
from sct.analyses.elevation_notch.testing import (
    run_notch_api,
    run_notch_cli,
    validate_notch_results,
)
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis

ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(
        config=SCTElevationNotchAnalysisConfig,
        cli_command=notch_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_notch_api,
            cli_runner=run_notch_cli,
            validator=validate_notch_results,
        ),
    ),
)

__all__ = ["full_elevation_notch_analysis"]
