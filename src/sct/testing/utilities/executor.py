# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Supported Analyses Executor"""

from __future__ import annotations

from pathlib import Path

from sct.configuration.logger import sct_logger
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import ANALYSIS_REGISTRY
from sct.testing.utilities.common import TestParams


def execute_analysis_test(
    test_params: TestParams,
    output_dir: Path,
    graphs: bool = False,
    cli: bool = False,
) -> None:
    """Analysis execution function for testing module.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    graphs : bool, optional
        flag to enable graphs generation, by default False
    cli : bool, optional
        flag to enable cli usage instead of api, by default False

    Raises
    ------
    ValueError
        unsupported analysis type
    """

    handler: AnalysisHandler | None = ANALYSIS_REGISTRY.get(test_params.analysis)
    if handler is None:
        raise ValueError(f"Unsupported analysis type: {test_params.analysis}")

    testing_handler: AnalysisTestingHandler | None = handler.testing

    if handler is None:
        raise ValueError(f"Unsupported analysis type: {test_params.analysis}")

    if testing_handler is None:
        raise ValueError(f"Unsupported testing for analysis type: {test_params.analysis}")

    if cli:
        results = testing_handler.cli_runner(
            params=test_params,
            output_dir=output_dir,
            config=test_params.config,
            graphs=graphs,
        )
    else:
        config = handler.config.from_toml(test_params.config) if test_params.config is not None else handler.config()
        results = testing_handler.api_runner(
            params=test_params,
            output_dir=output_dir,
            config=config,
            graphs=graphs,
        )

    sct_logger.info("Validating results...")
    testing_handler.validator(results, test_params.reference_output)
