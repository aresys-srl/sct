# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Spectral Analysis - Core implementation"""

from sct.analyses.spectra.core.analysis import (
    sct_distributed_spectral_analysis,
    sct_point_target_spectral_analysis,
)

__all__ = ["sct_distributed_spectral_analysis", "sct_point_target_spectral_analysis"]
