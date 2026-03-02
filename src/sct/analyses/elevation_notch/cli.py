# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Command Line Interface
----------------------
"""

from __future__ import annotations

from pathlib import Path

import click

from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger


@click.command(name="notch-analysis")
@common.input_product_option
@common.output_directory_option
@click.option(
    "--antenna-pattern",
    "-ap",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Path to the antenna pattern NetCDF file",
)
@common.generate_graph_option
@common.share_config
def notch_analysis(
    config: GeneralConfiguration,
    product: Path,
    output_directory: Path,
    antenna_pattern: Path | None,
    graphs: bool,
) -> None:
    """Elevation Notch Analysis."""

    log_path = output_directory / "sct_notch_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")
        if antenna_pattern is not None:
            sct_logger.info(f"Antenna pattern: {antenna_pattern}")
        else:
            sct_logger.warning("No antenna pattern provided, only parabolic fit around minimum will be performed.")
        sct_logger.info(f"Output folder: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        common.display_title("Elevation  Notch  Analysis")

        analysis_config = (
            SCTElevationNotchAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTElevationNotchAnalysisConfig()
        )
        elevation_notch_analysis_implementation(
            product=product,
            antenna_pattern=antenna_pattern,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("Elevation Notch Analysis")
@common.graceful_exit("Elevation Notch Analysis")
def elevation_notch_analysis_implementation(
    product: Path,
    antenna_pattern: Path | None,
    output_directory: Path,
    config: SCTElevationNotchAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the elevation notch analysis command."""
    from sct.analyses.elevation_notch.main import full_elevation_notch_analysis

    full_elevation_notch_analysis(
        product=product,
        antenna_pattern=antenna_pattern,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )
