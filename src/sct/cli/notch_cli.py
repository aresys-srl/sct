# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Elevation Notch Analysis commands.
--------------------------------------
"""

import sys
from collections.abc import Callable
from pathlib import Path

import click

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration
from sct.orchestration import full_elevation_notch_analysis_implementation


def import_plot_elevation_notch_analysis() -> Callable:
    """Import the generate_coherence_graphs plotting function."""
    try:
        from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return plot_elevation_notch_analysis


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
def pt_notch_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    antenna_pattern: Path | None,
    graphs: bool,
) -> None:
    """Elevation Notch Analysis."""

    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_notch_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    if antenna_pattern is not None:
        sct_logger.info(f"Antenna pattern: {antenna_pattern}")
    else:
        sct_logger.warning("No antenna pattern provided, only parabolic fit around minimum will be performed.")
    sct_logger.info(f"Output folder: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Elevation  Notch  Analysis")

    elevation_notch_analysis_implementation(
        product=product,
        antenna_pattern=antenna_pattern,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("Elevation Notch Analysis")
@common.graceful_exit("Elevation Notch Analysis", "elevation_notch_analysis")
def elevation_notch_analysis_implementation(
    product: Path, antenna_pattern: Path | None, output_directory: Path, config: SCTConfiguration, graphs: bool
) -> None:
    """Implement the elevation notch analysis command."""
    full_elevation_notch_analysis_implementation(
        product=product,
        antenna_pattern=antenna_pattern,
        output_directory=output_directory,
        config=config,
        graphs_func=import_plot_elevation_notch_analysis() if graphs else None,
    )
