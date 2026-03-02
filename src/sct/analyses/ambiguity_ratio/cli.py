# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Command Line Interface
----------------------
"""

from __future__ import annotations

from pathlib import Path

import click

from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger


@click.command(name="ptar-analysis")
@common.input_product_option
@common.input_point_target_option
@common.output_directory_option
@common.share_config
def pt_ambiguity_ratio_analysis(
    config: GeneralConfiguration,
    product: Path,
    point_target_source: Path,
    output_directory: Path,
) -> None:
    """Point Target Ambiguity Ratio Analysis."""
    log_path = output_directory / "sct_tar_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")
        sct_logger.info(f"Point targets: {point_target_source}")
        sct_logger.info(f"Output folder: {output_directory}")

        common.display_title("Ambiguity  Ratio  Analysis")

        analysis_config = (
            SCTTargetAmbiguityRatioConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTTargetAmbiguityRatioConfig()
        )
        pt_ambiguity_ratio_analysis_implementation(
            product=product,
            point_target_source=point_target_source,
            output_directory=output_directory,
            config=analysis_config,
            graphs=True,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("Point Target Ambiguity Ratio Analysis")
@common.graceful_exit("Point Target Ambiguity Ratio Analysis")
def pt_ambiguity_ratio_analysis_implementation(
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    config: SCTTargetAmbiguityRatioConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the point target ambiguity ratio analysis command."""
    from sct.analyses.ambiguity_ratio.main import full_pt_ambiguity_ratio_analysis

    full_pt_ambiguity_ratio_analysis(
        product=product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )
