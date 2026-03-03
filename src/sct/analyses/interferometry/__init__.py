# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Interferometric Analysis
------------------------------
"""

from __future__ import annotations

from sct.analyses.interferometry.cli import interf_coherence_analysis
from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig
from sct.analyses.interferometry.main import full_interferometric_analysis
from sct.analyses.interferometry.testing import (
    run_interf_api,
    run_interf_cli,
    validate_interf_results,
)
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis

ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(
        config=SCTInterferometricAnalysisConfig,
        cli=interf_coherence_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_interf_api,
            cli_runner=run_interf_cli,
            validator=validate_interf_results,
        ),
    ),
)

__all__ = ["full_interferometric_analysis"]
