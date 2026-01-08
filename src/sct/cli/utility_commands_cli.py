# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Utility Commands.
---------------------
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from arepytools.timing.precisedatetime import PreciseDateTime
from perseo_perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters
from perseo_perturbations.atmospheric.troposphere import TroposphericGRIDResolution

from sct import __version__
from sct.cli import common
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.io.input_product_plugins import import_input_product_plugins
from sct.io.point_target_manager import convert_rosamond_file_to_compliant_csv
from sct.testing.run import run_tests, summary_results
from sct.web_scraping.cddis_downloader import InvalidCDDISRequest
from sct.web_scraping.ionosphere_tec_map_downloader import download_ionospheric_tec_maps
from sct.web_scraping.troposphere_maps_downloader import download_tropospheric_products

if TYPE_CHECKING:
    import datetime

enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")

try:
    import click
except ImportError:
    sct_logger.critical('Install cli requirements "pip install sct[cli]"')
    sys.exit(1)


def convert_rosamond_csv() -> None:
    """Entry point for the Rosamond .csv converter utility."""
    sct_rosamond_dataset_converter()


def download_ionex_tec_maps() -> None:
    """Entry point for downloading IONEX TEC maps for Ionospheric Perturbation computation."""
    sct_ionex_map_downloader()


def download_tropospheric_vmf3_maps() -> None:
    """Entry point for downloading Tropospheric Products for VMF3 Perturbation computation."""
    sct_tropospheric_map_downloader()


def integration_testing() -> None:
    """Entry point for sct integration testing module using test registry."""
    sct_integration_testing_run()


date_option = click.option(
    "--date",
    "-d",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d %H:%M:%S"]),
    help='Reference date in "2024-04-20 10:00:00" format',
)


# ROSAMOND DATA CONVERTER
@click.command(
    name="sct-rosamond-data-to-csv",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the downloaded Rosamond dataset .csv",
)
@date_option
@click.option(
    "--output_directory",
    "-out",
    required=False,
    default=None,
    type=click.Path(path_type=Path, exists=True, dir_okay=True),
    help="Path to the folder where to save output data",
)
def sct_rosamond_dataset_converter(
    source: Path,
    date: datetime.datetime,
    output_directory: Path | None,
) -> None:
    """Convert downloaded Rosamond Point Targets dataset .csv file to SCT compliant .csv file."""
    if output_directory is None:
        output_directory = source.parent

    acq_date = PreciseDateTime.from_numeric_datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
    )

    click.echo("Converting original Rosamond dataset to SCT .csv compliant template...")
    rosamond_data = convert_rosamond_file_to_compliant_csv(df=source, measurement_date=acq_date)
    outfile = output_directory.joinpath("rosamond_point_target.csv")
    rosamond_data.to_csv(outfile, index=False)
    click.echo(f"Output file can be found here {outfile}.")


# IONOSPHERIC MAPS DOWNLOAD
@click.command(
    name="sct-ionospheric-maps-download",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@date_option
@click.option(
    "--analysis-center",
    "-c",
    required=True,
    type=click.STRING,
    help="TEC Map analysis center, one of [COD, COR, EHR, ESA, ESR, IGR, IGS, JPL, UPC, UHR, UPR, UQR]",
)
@click.option(
    "--email",
    "-e",
    required=True,
    type=click.STRING,
    help="Authentication e-mail used to login to the CDDIS archive",
)
@common.output_directory_option
def sct_ionex_map_downloader(
    date: datetime.datetime,
    analysis_center: str,
    email: str,
    output_directory: Path,
) -> None:
    """Download IONEX TEC maps from NASA/CDDIS archive."""
    try:
        center = IonosphericAnalysisCenters[analysis_center.upper()]
    except KeyError:
        click.echo("Wrong center name. Check the --help section to see available analysis centers")
        sys.exit(-1)

    click.echo("Downloading IONEX TEC maps from NASA/CDDIS archive...")
    acq_date = PreciseDateTime.from_numeric_datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
    )
    try:
        outfile = download_ionospheric_tec_maps(
            acq_date=acq_date,
            center=center,
            auth_email=email,
            output_dir=output_directory,
        )
        click.echo(f"Output file can be found here {outfile}.")
    except InvalidCDDISRequest:
        click.echo("ERROR: Invalid Request. Invalid e-mail or file requested does not exist.")
        sys.exit(-1)


# TROPOSPHERIC MAPS DOWNLOAD
@click.command(
    name="sct-tropospheric-maps-download",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@date_option
@click.option(
    "--resolution",
    "-r",
    required=True,
    type=click.STRING,
    help="Grid resolution for the VMF3 map, one of [FINE, COARSE]",
)
@common.output_directory_option
def sct_tropospheric_map_downloader(
    date: datetime.datetime,
    resolution: str,
    output_directory: Path,
) -> None:
    """Download VMF3 Tropospheric Products."""
    try:
        grid_res = TroposphericGRIDResolution[resolution.upper()]
    except KeyError:
        click.echo("Wrong grid resolution. Check the --help section to see available resolutions")
        sys.exit(-1)

    click.echo("Downloading VMF3 tropospheric products...")
    acq_date = PreciseDateTime.from_numeric_datetime(
        date.year,
        date.month,
        date.day,
        date.hour,
        date.minute,
        date.second,
    )

    outfiles = download_tropospheric_products(
        acq_date=acq_date,
        map_grid_resolution=grid_res,
        output_dir=output_directory,
    )
    click.echo("Output files can be found here:")
    for file in outfiles:
        click.echo(str(file))


# INTEGRATIONS TESTING
@click.command(
    name="sct-testing",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--registry",
    "-r",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=False),
    help="Path to the testing registry containing the tests to be run",
)
@click.option(
    "--output_directory",
    "-out",
    required=False,
    default=None,
    type=click.Path(path_type=Path, dir_okay=True),
    help="Path to the folder where to save output data",
)
@click.option(
    "--cli",
    "-c",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to perform analysis using the SCT CLI tool instead of the API",
)
@common.generate_graph_option
def sct_integration_testing_run(registry: Path, output_directory: Path, cli: bool, graphs: bool) -> None:
    """Run SCT integration tests procedure from registry."""
    common.display_title("SCT Integration Tests")

    click.echo(f"SCT Version: {__version__}\n")

    click.echo("Installed plugins detected:\n")

    for name in import_input_product_plugins(additional_plugins=[]):
        click.echo(name)
        click.echo()

    if not output_directory.exists():
        click.echo("Output directory not found: creating the output folder.")
        output_directory.mkdir(parents=True)

    results = run_tests(registry_path=registry, output_dir=output_directory, cli=cli, graphs=graphs)

    common.display_title("Summary")

    outcome = summary_results(results=results)

    if outcome:
        sys.exit(0)
    else:
        sys.exit(-1)
