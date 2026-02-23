# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Supported Analyses Handler definition"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sct.configuration.sct_configuration import SCTConfiguration
from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams


@dataclass
class AnalysisHandler:
    """Analysis handler definition"""

    api_runner: Callable[[TestParams, Path, SCTConfiguration | None, bool], TestOutput]
    cli_runner: Callable[[TestParams, Path, Path | None, bool], TestOutput]
    validator: Callable[[TestOutput, ReferenceOutput], None]
