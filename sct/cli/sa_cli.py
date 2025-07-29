# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Spectral Analysis commands
------------------------------
"""

import sys
import time
from pathlib import Path

import art
import click
import numpy as np

from sct.analyses.spectral_analysis import sct_point_target_spectral_analysis
from sct.configuration.logger import SCTFileHandler, enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)


@click.command(name="spectral-analysis")
@click.option(
    "--product",
    "-p",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the product to be analyzed",
)
@click.option(
    "--point-target-source",
    "-pt",
    required=True,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the external point target source",
)
@click.option(
    "--output_directory",
    "-out",
    required=True,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the folder where to save output data",
)
@share_config
def spectral_pt_analysis(
    config: SCTConfiguration,
    product: Path,
    point_target_source: Path,
    output_directory: Path,
) -> None:
    # saving log file to output folder
    if config.general.save_log:
        logging_file_handler = SCTFileHandler(filename=output_directory.joinpath("sct_spectral_analysis.log"))
        enable_quality_logger(file_handler=logging_file_handler)
        sct_logger.addHandler(logging_file_handler)
    else:
        enable_quality_logger()

    # inheriting configuration settings from group command in CLI main
    config_sa = config.spectral_analysis

    try:
        from arepyextras.quality.spectral_analysis.graphical_output import spectral_graphs

    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    sct_logger.info(f"Output folder is: {output_directory}")

    sct_logger.info(f"External point target source provided: {point_target_source}")

    sct_logger.info(f"Selected product is: {product}")

    click.echo("\n")
    txt = art.text2art("Spectral  Analysis", font="doom")
    click.echo(txt + "\n")

    start = time.perf_counter()
    output = sct_point_target_spectral_analysis(
        product_path=product, external_target_source=point_target_source, config=config_sa
    )

    sct_logger.info("Generating graphs...")
    spectral_graphs(data=output, output_dir=output_directory, graph_type="POINT")

    elapsed = np.round(time.perf_counter() - start, 2)
    sct_logger.info(f"Point Target Spectral Analysis completed in {elapsed} s.")
