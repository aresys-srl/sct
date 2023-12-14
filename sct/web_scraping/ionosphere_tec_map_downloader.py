# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Ionosphere TEC maps downloader
------------------------------
"""

import time
from enum import Enum
from pathlib import Path
from typing import Union

from arepyextras.perturbations.atmospheric import GPS_WEEK_REFERENCE
from arepyextras.perturbations.atmospheric.ionosphere import (
    IonosphericAnalysisCenters,
    TECMapSolutionType,
    TECMapTimeResolution,
    generate_ionospheric_map_filename,
)
from arepytools.timing.conversions import date_to_gps_week
from arepytools.timing.precisedatetime import PreciseDateTime
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from sct.web_scraping import url_sep
from sct.web_scraping._utilities import download_watchdog

_COMPRESSED_FILE_EXTENSION_OLD = ".Z"
_COMPRESSED_FILE_EXTENSION_NEW = ".gz"


class IonosphericWebArchives(Enum):
    """Ionospheric web archives where to download data from"""

    CDDIS = r"https://cddis.nasa.gov/archive/gnss/products/ionex"


auth = HTTPBasicAuth("giopar", "47m05ph3r1c_Corrs")


def _generate_download_link(acq_time: PreciseDateTime, map_name: str) -> str:
    """Generate url to the TEC map to be downloaded from the CDDIS archive.

    Parameters
    ----------
    acq_time : PreciseDateTime
        acquisition time
    map_name : str
        name of the TEC map to be downloaded

    Returns
    -------
    str
        complete url to download the compressed map
    """
    url = url_sep.join(
        [
            IonosphericWebArchives.CDDIS.value,
            str(acq_time.year),
            f"{acq_time.day_of_the_year:03}",
            map_name,
        ]
    )
    gps_week, _ = date_to_gps_week(acq_time)
    if gps_week < GPS_WEEK_REFERENCE:
        return url + _COMPRESSED_FILE_EXTENSION_OLD

    return url + _COMPRESSED_FILE_EXTENSION_NEW


def download_ionospheric_tec_maps(
    acq_date: PreciseDateTime, center: IonosphericAnalysisCenters, output_dir: Union[str, Path]
) -> Path:
    """Fetching the ionospheric map for the acquisition time and analysis center provided from NASA CDDIS archive.

    Parameters
    ----------
    acq_date : str
        time of interest to retrieve the correct ionospheric data
    center : PreciseDateTime
        ionospheric map analysis center
    output_dir : Union[str, Path]
        path to output directory where to save downloaded file

    Returns
    -------
    Path
        path to the downloaded map
    """
    output_dir = Path(output_dir)

    map_name = generate_ionospheric_map_filename(acq_time=acq_date, center=center)
    download_link = _generate_download_link(acq_time=acq_date, map_name=map_name)

    downloaded_file = output_dir.joinpath(download_link.split(url_sep)[-1])

    # init of chrome web driver headless and with custom download folder
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(output_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        },
    )

    # opening browser and reach the site
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get(IonosphericWebArchives.CDDIS.value)

    # filling authentication form
    user_form = browser.find_element(By.ID, "username")
    pwd_form = browser.find_element(By.ID, "password")
    user_form.click()
    user_form.clear()
    user_form.send_keys(auth.username)
    pwd_form.click()
    pwd_form.clear()
    pwd_form.send_keys(auth.password)

    # log in
    log_in = browser.find_element(By.NAME, "commit")
    log_in.click()

    # wait some time for authentication redirecting
    time.sleep(6)

    # get file
    browser.get(download_link)

    assert download_watchdog(directory=output_dir, n_files=1)

    return downloaded_file


# !!!
# it does not make sense to provide the user with a python object containing map data
# files only are needed to perform the analysis

# def get_ionex_tec_maps(
#     acq_time: PreciseDateTime,
#     analysis_center: IonosphericAnalysisCenters,
#     solution_type: TECMapSolutionType = TECMapSolutionType.FINAL,
#     time_resolution: TECMapTimeResolution = TECMapTimeResolution.HOUR,
# ):
#
#     map_name = generate_ionospheric_map_filename(
#         acq_time=acq_time, center=analysis_center, solution_type=solution_type, time_resolution=time_resolution
#     )


if __name__ == "__main__":
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    date = PreciseDateTime.from_utc_string("04-JAN-2023 08:41:34.530204377325")
    download_ionospheric_tec_maps(acq_date=date, center=IonosphericAnalysisCenters.COD, output_dir=out_dir)
