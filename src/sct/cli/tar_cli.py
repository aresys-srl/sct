# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Target Ambiguity Ratio Analysis commands.
---------------------------------------------
"""

import sys
from pathlib import Path

import click

from sct.analyses.ambiguity_ratio_analysis import sct_point_target_ambiguity_ratio_analysis
from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


@click.command(name="ptar-analysis")
@common.input_product_option
@common.input_point_target_option
@common.output_directory_option
@common.share_config
def pt_ambiguity_ratio_analysis(
    config: SCTConfiguration,
    product: Path,
    point_target_source: Path,
    output_directory: Path,
) -> None:
    """Point Target Ambiguity Ratio Analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_tar_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Point targets: {point_target_source}")
    sct_logger.info(f"Output folder: {output_directory}")

    common.display_title("Ambiguity  Ratio  Analysis")

    pt_ambiguity_ratio_analysis_implementation(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
    )


@common.log_elapsed_time("Point Target Ambiguity Ratio Analysis")
@common.graceful_exit("Point Target Ambiguity Ratio Analysis", "target_ambiguity_ratio_analysis")
def pt_ambiguity_ratio_analysis_implementation(
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    config: SCTConfiguration,
) -> None:
    """Implement the point target ambiguity ratio analysis command."""
    try:
        from perseo_quality.tar_analysis.graphical_output import ambiguities_graphs
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    output = sct_point_target_ambiguity_ratio_analysis(
        product_path=product,
        external_target_source=point_target_source,
        config=config.target_ambiguity_ratio_analysis,
    )
    sct_logger.info("Generating graphs...")
    ambiguities_graphs(data=output, output_dir=output_directory, graph_type="PTAR")
