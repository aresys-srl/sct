# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Command Line Interface
----------------------
"""

from __future__ import annotations

from pathlib import Path

import typer

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger


def spectral_analysis(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    point_target_source: common.InputPointTargetSource = None,
    graphs: common.GraphsOption = False,
) -> None:
    """Point and Distributed Target Spectral Analysis.

    \b
    It can be performed:
    - at each visible target location providing a point target source file -pt/--point-target-source
    - on distributed targets by partitioning the data into azimuth blocks/bursts
    """

    config: GeneralConfiguration = ctx.obj

    log_path = output_directory / "sct_spectral_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")

        if point_target_source is not None:
            sct_logger.info(f"Point targets: {point_target_source}")

        sct_logger.info(f"Output folder: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        if point_target_source is not None:
            common.display_title("PT  Spectral  Analysis")
        else:
            common.display_title("Distrib.  Spectral  Analysis")

        analysis_config = (
            SCTSpectralAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTSpectralAnalysisConfig()
        )
        spectral_analysis_implementation(
            product=product,
            point_target_source=point_target_source,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("Point Target Spectral Analysis")
@common.graceful_exit("Point Target Spectral Analysis")
def spectral_analysis_implementation(
    product: Path,
    point_target_source: Path | None,
    output_directory: Path,
    config: SCTSpectralAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the spectral analysis command."""
    from sct.analyses.spectra.main import full_spectral_analysis

    full_spectral_analysis(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )
