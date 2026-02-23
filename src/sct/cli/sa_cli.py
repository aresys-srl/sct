# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Spectral Analysis commands
------------------------------
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import click

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


def import_spectral_graphs_func() -> Callable:
    """Loading the spectral analysis graphs plotting function."""
    try:
        from perseo_quality.spectral_analysis.graphical_output import spectral_graphs
    except ImportError:
        sct_logger.critical('Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return spectral_graphs


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def spectral_analysis(config) -> None:
    """Spectral Analysis."""


@spectral_analysis.command("point-target")
@common.input_product_option
@common.input_point_target_option
@common.output_directory_option
@common.generate_graph_option
@common.share_config
def spectral_pt_analysis(
    config: SCTConfiguration,
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    graphs: bool,
) -> None:
    """Point Target Spectral Analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_spectral_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Point targets: {point_target_source}")
    sct_logger.info(f"Output folder: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("PT  Spectral  Analysis")

    spectral_analysis_implementation(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@spectral_analysis.command("distributed")
@common.input_product_option
@common.output_directory_option
@common.generate_graph_option
@common.share_config
def spectral_analysis_distributed(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    graphs: bool,
) -> None:
    """Distributed Spectral Analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_spectral_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Output folder: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Distrib.  Spectral  Analysis")

    spectral_analysis_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
        point_target_source=None,
    )


@common.log_elapsed_time("Point Target Spectral Analysis")
@common.graceful_exit("Point Target Spectral Analysis", "spectral_analysis")
def spectral_analysis_implementation(
    product: Path,
    point_target_source: Path | None,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the spectral analysis command."""
    from sct.orchestration import full_spectral_analysis_implementation

    full_spectral_analysis_implementation(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs_func=import_spectral_graphs_func() if graphs else None,
    )
