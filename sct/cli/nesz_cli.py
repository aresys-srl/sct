# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI NESZ Analysis commands
--------------------------
"""

import logging
import sys
import time
from pathlib import Path

import art
import click
from arepyextras.quality.nesz_analysis.analysis import save_to_netcdf

import sct.analyses.nesz_analysis as nesz_func
from sct.configuration.sct_default_configuration import SCTConfiguration

# syncing with logger
log = logging.getLogger("quality_analysis")

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)


@click.command(name="nesz_analysis")
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
    "--graphs",
    "-g",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to generate graphical output at the end of the analysis",
)
@share_config
def nesz_analysis(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    external_orbit: Path,
    graphs: bool,
):
    """Noise Equivalent Sigma-Zero Analysis"""

    # inheriting configuration settings from group command in CLI main
    config_nesz = config.nesz_analysis

    if graphs:
        try:
            from arepyextras.quality.nesz_analysis.graphical_output import nesz_graphs

        except ImportError:
            log.critical('Install cli requirements "pip install sct[graphs]"')
            sys.exit(1)

    log.info(f"Output folder is: {output_directory}")
    log.info(f"Selected product is: {product}")
    click.echo("\n")
    txt = art.text2art("NESZ  Analysis", font="slant")
    click.echo(txt + "\n")
    start = time.perf_counter_ns()

    # performing nesz analysis
    data = nesz_func.main(product_path=product, config=config_nesz, external_orbit_path=external_orbit)

    # saving results to .nc file
    log.info("Saving data to netCDF format...")
    save_to_netcdf(data=data, out_path=output_directory)

    if graphs:
        log.info("Plotting graphs...")
        for item in data:
            try:
                nesz_graphs(data=item, output_dir=output_directory)
            except Exception as err:
                log.error(f"Cannot create graph for {item.channel}, {item.polarization}")
                log.error(err)

    elapsed = (time.perf_counter_ns() - start) / 1e9
    log.info(f"NESZ Analysis completed in {elapsed} s.")
