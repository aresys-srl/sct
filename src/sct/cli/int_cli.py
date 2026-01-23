# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Interferometric Analysis commands.
--------------------------------------
"""

import sys
from collections.abc import Callable
from pathlib import Path

import click

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration
from sct.orchestration import full_interferometric_analysis_implementation


def import_generate_coherence_graphs() -> Callable:
    """Import the generate_coherence_graphs plotting function."""
    try:
        from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return generate_coherence_graphs


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
    config: SCTConfiguration,
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
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_interf_analysis.log"))
        if config.general.save_log
        else None
    )
    enable_quality_logger(file_handler)

    if product_2:
        sct_logger.info(f"First co-registered product: {product}")
        sct_logger.info(f"Second co-registered product: {product_2}")
    else:
        sct_logger.info(f"Interferogram product: {product}")
    sct_logger.info(f"Output folder is: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Interferometric Analysis")

    interf_coherence_analysis_implementation(
        product=product,
        product_2=product_2,
        config=config,
        output_directory=output_directory,
        graphs=graphs,
    )


@common.log_elapsed_time("Interferometric Analysis")
@common.graceful_exit("Interferometric Analysis", "interferometric_analysis")
def interf_coherence_analysis_implementation(
    product: Path,
    product_2: Path | None,
    config: SCTConfiguration,
    output_directory: Path,
    graphs: bool,
) -> None:
    """Implement of the interferometric analysis command."""
    full_interferometric_analysis_implementation(
        product=product,
        product_2=product_2,
        config=config,
        output_directory=output_directory,
        graphs_func=import_generate_coherence_graphs() if graphs else None,
    )
