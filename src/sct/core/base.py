# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Analyses Handler for registration"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from click import Command

from sct.testing.utilities.common import ReferenceOutput, TestOutput, TestParams


@dataclass
class AnalysisTestingHandler:
    """Analysis handler for testing definition"""

    api_runner: Callable[[TestParams, Path, Any | None, bool], TestOutput]
    cli_runner: Callable[[TestParams, Path, Path | None, bool], TestOutput]
    validator: Callable[[TestOutput, ReferenceOutput], None]


@dataclass
class AnalysisHandler:
    """Analysis handler definition"""

    config: Any
    cli_command: Command | None
    testing: AnalysisTestingHandler | None
