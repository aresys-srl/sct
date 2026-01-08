# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Elevation Notch Analysis commands.
--------------------------------------
"""

import sys
from pathlib import Path

import click
from perseo_quality.elevation_notch_analysis.support import elevation_notch_profiles_to_netcdf

from sct.analyses.elevation_notch import sct_elevation_notch_analysis
from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


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
@common.graceful_exit("Elevation Notch Analysis", "target_ambiguity_ratio_analysis")
def elevation_notch_analysis_implementation(
    product: Path, antenna_pattern: Path | None, output_directory: Path, config: SCTConfiguration, graphs: bool
) -> None:
    """Implement the elevation notch analysis command."""
    try:
        from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    output = sct_elevation_notch_analysis(
        product_path=product, antenna_pattern_file=antenna_pattern, config=config.elevation_notch_analysis
    )
    sct_logger.info("Saving results to NetCDF...")
    elevation_notch_profiles_to_netcdf(data=output, output_dir=output_directory)
    if graphs:
        sct_logger.info("Generating graphs...")
        output_graphs_dir = output_directory.joinpath("graphs")
        output_graphs_dir.mkdir(exist_ok=True)
        plot_elevation_notch_analysis(data=output, output_dir=output_graphs_dir)
