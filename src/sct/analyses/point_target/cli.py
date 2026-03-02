# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Command Line Interface
----------------------
"""

from __future__ import annotations

from pathlib import Path

import click

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger


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
    config: GeneralConfiguration,
    product: Path,
    output_directory: Path,
    external_orbit: Path,
    external_corrections_product: Path,
    point_target_source: Path,
    graphs: bool,
) -> None:
    """Point Target Analysis (IRF, Localization and RCS)."""

    log_path = output_directory / "sct_pta_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
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

        analysis_config = (
            SCTPointTargetAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTPointTargetAnalysisConfig()
        )
        target_analysis_implementation(
            product=product,
            external_orbit=external_orbit,
            external_corrections_product=external_corrections_product,
            point_target_source=point_target_source,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("Point Target Analysis")
@common.graceful_exit("Point Target Analysis")
def target_analysis_implementation(
    product: Path,
    external_orbit: Path | None,
    external_corrections_product: Path | None,
    point_target_source: Path,
    output_directory: Path,
    config: SCTPointTargetAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the point target analysis command."""
    from sct.analyses.point_target.main import full_point_target_analysis

    full_point_target_analysis(
        product=product,
        external_orbit=external_orbit,
        external_corrections_product=external_corrections_product,
        point_target_source=point_target_source,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )
