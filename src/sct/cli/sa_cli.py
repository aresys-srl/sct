# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Spectral Analysis commands
------------------------------
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def spectral_analysis(config) -> None:
    """Spectral Analysis."""


@spectral_analysis.command("point-target")
@common.input_product_option
@common.input_point_target_option
@common.output_directory_option
@common.share_config
def spectral_pt_analysis(
    config: SCTConfiguration,
    product: Path,
    point_target_source: Path,
    output_directory: Path,
) -> None:
    """Point Target Spectral Analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_pt_spectral_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Point targets: {point_target_source}")
    sct_logger.info(f"Output folder: {output_directory}")

    common.display_title("PT  Spectral  Analysis")

    spectral_pt_analysis_implementation(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
    )


@spectral_analysis.command("distributed")
@common.input_product_option
@common.output_directory_option
@common.share_config
def spectral_analysis_distributed(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
) -> None:
    """Distributed Spectral Analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_distributed_spectral_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Output folder: {output_directory}")

    common.display_title("Distrib.  Spectral  Analysis")

    spectral_distributed_analysis_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
    )


@common.log_elapsed_time("Point Target Spectral Analysis")
@common.graceful_exit("Point Target Spectral Analysis", "spectral_analysis")
def spectral_pt_analysis_implementation(
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    config: SCTConfiguration,
) -> None:
    """Implement the point target spectral analysis command."""
    try:
        from perseo_quality.spectral_analysis.graphical_output import spectral_graphs
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    from sct.analyses.spectral_analysis import sct_point_target_spectral_analysis

    output = sct_point_target_spectral_analysis(
        product_path=product,
        external_target_source=point_target_source,
        config=config.spectral_analysis,
    )
    sct_logger.info("Generating graphs...")
    spectral_graphs(data=output, output_dir=output_directory)


@common.log_elapsed_time("Distributed Spectral Analysis")
@common.graceful_exit("Distributed Spectral Analysis", "spectral_analysis")
def spectral_distributed_analysis_implementation(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
) -> None:
    """Implement the distributed spectral analysis command."""
    try:
        from perseo_quality.spectral_analysis.graphical_output import spectral_graphs
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    from sct.analyses.spectral_analysis import sct_distributed_spectral_analysis

    output = sct_distributed_spectral_analysis(
        product_path=product,
        config=config.spectral_analysis,
    )
    sct_logger.info("Generating graphs...")
    spectral_graphs(data=output, output_dir=output_directory)
