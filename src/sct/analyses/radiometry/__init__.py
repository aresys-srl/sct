# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Radiometric Analysis
--------------------------
"""

from __future__ import annotations

from sct.analyses.radiometry.cli import radiometric_analysis
from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.analyses.radiometry.main import (
    full_average_elevation_profiles_analysis,
    full_nesz_analysis,
    full_scalloping_analysis,
)
from sct.analyses.radiometry.testing import (
    run_nesz_api,
    run_nesz_cli,
    run_rain_forest_api,
    run_rain_forest_cli,
    validate_ra_results,
)
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis

ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME + "-nesz",
    handler=AnalysisHandler(
        config=SCTRadiometricAnalysisConfig,
        cli_command=radiometric_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_nesz_api,
            cli_runner=run_nesz_cli,
            validator=validate_ra_results,
        ),
    ),
)

register_analysis(
    analysis_type=ANALYSIS_NAME + "-rain-forest",
    handler=AnalysisHandler(
        config=SCTRadiometricAnalysisConfig,
        cli_command=radiometric_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_rain_forest_api,
            cli_runner=run_rain_forest_cli,
            validator=validate_ra_results,
        ),
    ),
)

register_analysis(
    analysis_type=ANALYSIS_NAME + "-scalloping",
    handler=AnalysisHandler(config=SCTRadiometricAnalysisConfig, cli_command=radiometric_analysis, testing=None),
)

__all__ = [
    "full_nesz_analysis",
    "full_average_elevation_profiles_analysis",
    "full_scalloping_analysis",
]
