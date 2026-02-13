# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Point Target Analysis commands
----------------------------------
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import click

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


def import_pta_graphs_function() -> Callable:
    """Import the point target analysis plotting function."""
    try:
        from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return point_target_graphs_generation


@click.command(name="target-analysis")
@common.input_product_option
@common.output_directory_option
@click.option(
    "--external-orbit",
    "-eo",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the external orbit file",
)
@click.option(
    "--external-corrections-product",
    "-ec",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the external ALE corrections product",
)
@common.input_point_target_option
@common.generate_graph_option
@common.share_config
def target_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    external_orbit: Path,
    external_corrections_product: Path,
    point_target_source: Path,
    graphs: bool,
) -> None:
    """Point Target Analysis (IRF, Localization and RCS)."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_pta_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    if external_orbit:
        sct_logger.info(f"External orbit: {external_orbit}")
    else:
        sct_logger.info("No external orbit provided, using orbit from product.")

    if external_corrections_product:
        sct_logger.info(f"External ALE Corrections Product: {external_corrections_product}")

    sct_logger.info(f"Point targets: {point_target_source}")
    sct_logger.info(f"Output folder: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Point Target Analysis")

    target_analysis_implementation(
        product=product,
        external_orbit=external_orbit,
        external_corrections_product=external_corrections_product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("Point Target Analysis")
@common.graceful_exit("Point Target Analysis", "point_target_analysis")
def target_analysis_implementation(
    product: Path,
    external_orbit: Path | None,
    external_corrections_product: Path | None,
    point_target_source: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the point target analysis command."""
    point_target_graphs_generation = None
    if graphs:
        point_target_graphs_generation = import_pta_graphs_function()

    from sct.orchestration import full_point_target_analysis_implementation

    full_point_target_analysis_implementation(
        product=product,
        external_orbit=external_orbit,
        external_corrections_product=external_corrections_product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs_func=point_target_graphs_generation,
    )
