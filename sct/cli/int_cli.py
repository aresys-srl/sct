# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Interferometric Analysis commands
-------------------------------------
"""
import logging
import sys
import time
from pathlib import Path

import art
import click
from arepyextras.quality.core.custom_logger import CustomFormatterFileHandler
from arepyextras.quality.interferometric_analysis.support import coherence_histograms_to_netcdf

import sct.analyses.interferometric_analysis as intf
from sct.configuration.sct_configuration import SCTConfiguration

# syncing with logger
log = logging.getLogger("quality_analysis")

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)


@click.command(name="interferometric-analysis")
@click.option(
    "--product",
    "-p",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the interferogram product or to the co-registered product to be analyzed",
)
@click.option(
    "--output_directory",
    "-out",
    required=True,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the folder where to save output data",
)
@click.option(
    "--product_2",
    "-pp",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Second co-registered product, must be provided if the first product is not an interferogram",
)
@click.option(
    "--graphs",
    "-g",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to generate graphical output at the end of the analysis",
)
@share_config
def interf_coherence_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    product_2: Path | None = None,
    graphs: bool = False,
):
    """Interferometric Analysis (Coherence and Coherence intensity 2D histograms)

    \b
    It can be performed using a single interferogram product, provided via -p/--product argument or by using two
    co-registered products, provided respectively with -p/--product and -pp/--product_2
    """

    # saving log file to output folder
    if config.general.save_log:
        logging_file_handler = logging.FileHandler(output_directory.joinpath("sct_pta_analysis.log"))
        logging_file_handler.setFormatter(CustomFormatterFileHandler())
        log.addHandler(logging_file_handler)

    # inheriting configuration settings from group command in CLI main
    config_interferometry = config.interferometric_analysis

    if graphs:
        try:
            from arepyextras.quality.interferometric_analysis.graphical_output import generate_coherence_graphs

        except ImportError:
            log.critical('Install graphs requirements "pip install sct[graphs]"')
            sys.exit(1)

    log.info(f"Output folder is: {output_directory}")
    log.info(f"Selected product is: {product}")

    click.echo("\n")
    txt = art.text2art("Interferometric  Analysis", font="doom")
    click.echo(txt + "\n")

    start = time.perf_counter_ns()
    coherence_res = intf.interferometric_coherence_analysis(
        product_path=product,
        second_product_path=product_2,
        config=config_interferometry,
    )

    # saving configuration used to output folder as .toml file
    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="interferometry")

    for res in coherence_res:
        # saving 2D histograms to netcdf
        coherence_histograms_to_netcdf(data=res, output_dir=output_directory)

    # graphical output management
    if graphs:
        log.info("Plotting graphs...")
        for res in coherence_res:
            generate_coherence_graphs(
                data=res, output_dir=output_directory, mode="magnitude", config=config_interferometry.base_config
            )
            generate_coherence_graphs(
                data=res, output_dir=output_directory, mode="phase", config=config_interferometry.base_config
            )

    elapsed = (time.perf_counter_ns() - start) / 1e9
    log.info(f"Interferometric Analysis completed in {elapsed} s.")
