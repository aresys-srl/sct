# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Point Target and Distributed Spectral Analysis
----------------------------------------------------
"""

from __future__ import annotations

from sct.analyses.spectra.cli import spectral_analysis
from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.analyses.spectra.main import full_spectral_analysis
from sct.analyses.spectra.testing import (
    run_spectral_api,
    run_spectral_cli,
    validate_spectral_results,
)
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis

ANALYSIS_NAME = __name__.split(".")[-1]


register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(
        config=SCTSpectralAnalysisConfig,
        cli=spectral_analysis,
        testing=AnalysisTestingHandler(
            api_runner=run_spectral_api,
            cli_runner=run_spectral_cli,
            validator=validate_spectral_results,
        ),
    ),
)

__all__ = ["full_spectral_analysis"]
