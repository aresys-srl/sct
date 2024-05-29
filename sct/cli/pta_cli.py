# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Point Target Analysis commands
----------------------------------
"""

import logging
import sys
import time
from pathlib import Path

import art
import click
from arepyextras.quality.core.custom_logger import CustomFormatterFileHandler

import sct.analyses.point_target_analysis as pta
from sct.configuration.sct_configuration import SCTConfiguration

# syncing with logger
log = logging.getLogger("quality_analysis")

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)


@click.command(name="target-analysis")
@click.option(
    "--product",
    "-p",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the product to be analyzed",
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
    "--external-orbit",
    "-eo",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the external orbit file",
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
    "--graphs",
    "-g",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to generate graphical output at the end of the analysis",
)
@share_config
def target_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    external_orbit: Path,
    point_target_source: Path,
    graphs: bool,
):
    """Point Target Analysis (IRF, Localization and RCS)"""

    # saving log file to output folder
    if config.general.save_log:
        logging_file_handler = logging.FileHandler(output_directory.joinpath("sct_pta_analysis.log"))
        logging_file_handler.setFormatter(CustomFormatterFileHandler())
        log.addHandler(logging_file_handler)

    # inheriting configuration settings from group command in CLI main
    config_pta = config.point_target_analysis

    if graphs:
        try:
            from sct.analyses.graphical_output import sct_pta_graphs

        except ImportError:
            log.critical('Install graphs requirements "pip install sct[graphs]"')
            sys.exit(1)

    log.info(f"Output folder is: {output_directory}")

    log.info(f"External point target source provided: {point_target_source}")

    log.info(f"Selected product is: {product}")

    click.echo("\n")
    txt = art.text2art("Point  Target  Analysis", font="doom")
    click.echo(txt + "\n")

    start = time.perf_counter_ns()
    results_df, graphs_data = pta.point_target_analysis_with_corrections(
        product_path=product,
        external_orbit_path=external_orbit,
        external_target_source=point_target_source,
        config=config_pta,
    )

    # saving results to csv file
    results_df.to_csv(output_directory.joinpath("point_target_analysis_results.csv"), index=False)

    # saving configuration used to output folder as .toml file
    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="point_target")

    # graphical output management
    if graphs:
        log.info("Plotting graphs...")
        graphs_out_dir = output_directory.joinpath("graphs")
        graphs_out_dir.mkdir(exist_ok=True)
        sct_pta_graphs(graphs_data=graphs_data, results_df=results_df, output_dir=graphs_out_dir)

    elapsed = (time.perf_counter_ns() - start) / 1e9
    log.info(f"Point Target Analysis completed in {elapsed} s.")
