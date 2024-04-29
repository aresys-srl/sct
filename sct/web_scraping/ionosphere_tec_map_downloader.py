# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Ionosphere TEC maps downloader
------------------------------
"""

from pathlib import Path

from arepyextras.perturbations.atmospheric import GPS_WEEK_REFERENCE
from arepyextras.perturbations.atmospheric.ionosphere import (
    IonosphericAnalysisCenters,
    generate_ionospheric_map_filename,
)
from arepytools.timing.conversions import date_to_gps_week
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.web_scraping.cddis_downloader import cddis_ftps_archive_downloader

_COMPRESSED_FILE_EXTENSION_OLD = ".Z"
_COMPRESSED_FILE_EXTENSION_NEW = ".gz"

_IONEX_ARCHIVE_PATH = "gnss/products/ionex"


def _generate_file_directory_on_server(acq_time: PreciseDateTime) -> str:
    """Generating the path to the correct folder on archive ftps server where the file to be downloaded is located.

    Parameters
    ----------
    acq_time : PreciseDateTime
        acquisition time of the desired product

    Returns
    -------
    str
        path to the parent folder on the server where the file to be downloaded is located
    """
    return "/".join([_IONEX_ARCHIVE_PATH, str(acq_time.year), f"{acq_time.day_of_the_year:03}"])


def _generate_product_archive_name(acq_time: PreciseDateTime, center: IonosphericAnalysisCenters) -> str:
    """Generating the name of the product to be downloaded with the corresponding archive extension.

    Parameters
    ----------
    acq_time : PreciseDateTime
        acquisition time of the desired product
    center : IonosphericAnalysisCenters
        ionospheric map analysis center

    Returns
    -------
    str
        name of the TEC map to be downloaded
    """
    map_name = generate_ionospheric_map_filename(acq_time=acq_time, center=center)
    gps_week, _ = date_to_gps_week(acq_time)
    if gps_week < GPS_WEEK_REFERENCE:
        return map_name + _COMPRESSED_FILE_EXTENSION_OLD

    return map_name + _COMPRESSED_FILE_EXTENSION_NEW


def download_ionospheric_tec_maps(
    acq_date: PreciseDateTime, center: IonosphericAnalysisCenters, auth_email: str, output_dir: str | Path
) -> Path:
    """Fetching the ionospheric map for the acquisition time and analysis center provided from NASA CDDIS archive.

    Parameters
    ----------
    acq_date : str
        time of interest to retrieve the correct ionospheric data
    center : PreciseDateTime
        ionospheric map analysis center
    auth_email : str
        authentication e-mail of the user registered on the CDDIS portal
    output_dir : str | Path
        path to output directory where to save downloaded file

    Returns
    -------
    Path
        path to the downloaded map
    """

    # generating the directory path on server where the product is located
    server_directory = _generate_file_directory_on_server(acq_time=acq_date)
    # generating name of the product to be downloaded
    map_name = _generate_product_archive_name(acq_time=acq_date, center=center)

    return cddis_ftps_archive_downloader(
        directory=server_directory, filename=map_name, email=auth_email, out_dir=output_dir
    )
