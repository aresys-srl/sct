# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Command Line Interface auxiliary utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from perseo_core.timing import PreciseDateTime
from perseo_perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters
from perseo_perturbations.atmospheric.troposphere import TroposphericGRIDResolution

from sct.cli import common
from sct.io.point_target_manager import convert_rosamond_file_to_compliant_csv
from sct.web_scraping.cddis_downloader import InvalidCDDISRequest
from sct.web_scraping.ionosphere_tec_map_downloader import download_ionospheric_tec_maps
from sct.web_scraping.troposphere_maps_downloader import download_tropospheric_products

utilities_app = typer.Typer(help="SCT Auxiliary CLI tools.")

DateOption = Annotated[
    datetime,
    typer.Option(
        ...,
        "--date",
        "-d",
        help='Reference date in "%Y-%m-%d %H:%M:%S" format',
    ),
]

SourceOption = Annotated[
    Path,
    typer.Option(
        ...,
        "--source",
        "-s",
        exists=True,
        dir_okay=False,
        file_okay=True,
        resolve_path=True,
        help="Path to the downloaded Rosamond dataset .csv",
    ),
]

AnalysisCenterOption = Annotated[
    str,
    typer.Option(
        ...,
        "--analysis-center",
        "-c",
        help="TEC Map analysis center, one of [COD, COR, EHR, ESA, ESR, IGR, IGS, JPL, UPC, UHR, UPR, UQR]",
    ),
]

EmailOption = Annotated[
    str,
    typer.Option(
        ...,
        "--email",
        "-e",
        help="Authentication e-mail used to login to the CDDIS archive",
    ),
]

ResolutionOption = Annotated[
    str,
    typer.Option(
        ...,
        "--resolution",
        "-r",
        help="Grid resolution for the VMF3 map, one of [FINE, COARSE]",
    ),
]


@utilities_app.command("rosamond-pt-converter")
def convert_rosamond_csv(
    source: SourceOption,
    date: DateOption,
    output_directory: common.OutputDirectoryOption = None,
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

    typer.echo("Converting original Rosamond dataset to SCT .csv compliant template...")
    rosamond_data = convert_rosamond_file_to_compliant_csv(df=source, measurement_date=acq_date)
    outfile = output_directory.joinpath("rosamond_point_target.csv")
    rosamond_data.to_csv(outfile, index=False)
    typer.echo(f"Output file can be found here {outfile}.")


@utilities_app.command("iono-downloader")
def download_ionex_tec_maps(
    date: DateOption,
    analysis_center: AnalysisCenterOption,
    email: EmailOption,
    output_directory: common.OutputDirectoryOption,
) -> None:
    """Download IONEX TEC maps from NASA/CDDIS archive."""
    try:
        center = IonosphericAnalysisCenters[analysis_center.upper()]
    except KeyError:
        typer.echo("Wrong center name. Check the --help section to see available analysis centers")
        utilities_app.Abort()

    typer.echo("Downloading IONEX TEC maps from NASA/CDDIS archive...")
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
        typer.echo(f"Output file can be found here {outfile}.")
    except InvalidCDDISRequest:
        typer.echo("ERROR: Invalid Request. Invalid e-mail or file requested does not exist.")
        utilities_app.Abort()


@utilities_app.command("tropo-downloader")
def download_tropospheric_vmf3_maps(
    date: DateOption,
    resolution: ResolutionOption,
    output_directory: common.OutputDirectoryOption,
) -> None:
    """Download VMF3 Tropospheric Products."""

    try:
        grid_res = TroposphericGRIDResolution[resolution.upper()]
    except KeyError:
        typer.echo("Wrong grid resolution. Check the --help section to see available resolutions")
        utilities_app.Abort()

    typer.echo("Downloading VMF3 tropospheric products...")
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
    typer.echo("Output files can be found here:")
    for file in outfiles:
        typer.echo(str(file))
