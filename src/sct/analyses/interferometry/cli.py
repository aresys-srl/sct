# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Command Line Interface
----------------------
"""

from __future__ import annotations

from pathlib import Path

import click

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger


@click.command(name="interferometric-analysis")
@click.option(
    "--product",
    "-p",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the interferogram product or to the co-registered product to be analyzed",
)
@common.output_directory_option
@click.option(
    "--product_2",
    "-pp",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Second co-registered product, must be provided if the first product is not an interferogram",
)
@common.generate_graph_option
@common.share_config
def interf_coherence_analysis(
    config: GeneralConfiguration,
    product: Path,
    output_directory: Path,
    product_2: Path | None = None,
    graphs: bool = False,
) -> None:
    """Interferometric Analysis (Coherence and Coherence intensity 2D histograms).

    \b
    It can be performed using a single interferogram product, provided via -p/--product argument or by using two
    co-registered products, provided respectively with -p/--product and -pp/--product_2
    """

    log_path = output_directory / "sct_interf_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        if product_2:
            sct_logger.info(f"First co-registered product: {product}")
            sct_logger.info(f"Second co-registered product: {product_2}")
        else:
            sct_logger.info(f"Interferogram product: {product}")
        sct_logger.info(f"Output folder is: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        common.display_title("Interferometric Analysis")

        analysis_config = (
            SCTInterferometricAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTInterferometricAnalysisConfig()
        )
        interf_coherence_analysis_implementation(
            product=product,
            product_2=product_2,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("Interferometric Analysis")
@common.graceful_exit("Interferometric Analysis")
def interf_coherence_analysis_implementation(
    product: Path,
    product_2: Path | None,
    config: SCTInterferometricAnalysisConfig,
    output_directory: Path,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement of the interferometric analysis command."""
    from sct.analyses.interferometry.main import full_interferometric_analysis

    full_interferometric_analysis(
        product=product,
        product_2=product_2,
        config=config,
        output_directory=output_directory,
        graphs=graphs,
    )
