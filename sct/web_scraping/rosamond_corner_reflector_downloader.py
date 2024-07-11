# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Automatic Rosamond (Calibration Site) coordinates download
----------------------------------------------------------
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from sct.io.point_target_manager import convert_rosamund_file_to_compliant_csv
from sct.web_scraping._utilities import download_watchdog

_ROSAMOND_CENTER_DOWNLOAD_WEBSITE = r"https://uavsar.jpl.nasa.gov/cgi-bin/calibration.pl"


class CornerReflectorCoordinatesType(Enum):
    """Corner Reflector coordinates types that can be downloaded"""

    INSTANTANEOUS_CRUST = "crust"
    MEAN_CRUST = "mean"
    TIDE_FREE = "tide-free"


def _datetime_formatting(acq_date: PreciseDateTime) -> str:
    """Converting the input PreciseDateTime format to the format needed by the date form on the website.

    Parameters
    ----------
    acq_date : PreciseDateTime
        input date to be reformatted

    Returns
    -------
    str
        formatted date
    """
    # composing date in format YYYY-MM-DD HH:MM
    date = datetime.strptime(str(acq_date)[:-6], "%d-%b-%Y %H:%M:%S.%f")

    return datetime.strftime(date, "%Y-%m-%d %H:%M")


def download_rosamond_corner_reflector_data(
    output_dir: Union[str, Path],
    acquisition_time: PreciseDateTime,
    coords_type: CornerReflectorCoordinatesType,
    timeout: int = 10,
) -> Path:
    """Download Rosamond corner reflector coordinates data at a given date directly from the official website.

    Parameters
    ----------
    output_dir : Union[str, Path]
        path to the download directory
    acquisition_time : PreciseDateTime
        date of interest
    coords_type : CornerReflectorCoordinatesType, optional
        type of coordinates to be downloaded, by default CornerReflectorCoordinatesType.INSTANTANEOUS_CRUST
    timeout : int, optional
        download watchdog timeout in seconds, by default 10

    Returns
    -------
    Path
        Path to the download file
    """

    output_dir = Path(output_dir)

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
    browser.get(_ROSAMOND_CENTER_DOWNLOAD_WEBSITE)

    # fill date form
    data_form = browser.find_element(By.ID, "date")
    data_form.click()
    data_form.clear()
    date = _datetime_formatting(acq_date=acquisition_time)
    data_form.send_keys(date)

    # select coordinates type
    coords_type_form = browser.find_element(By.ID, coords_type.value)
    coords_type_form.click()

    # download data
    get_data_button = browser.find_element(By.ID, "getDataButton")
    get_data_button.click()
    assert download_watchdog(directory=output_dir, n_files=1, timeout=timeout)
    browser.quit()

    # retrieve downloaded file path
    date_check = date.replace(" ", "_").replace(":", "")
    return [p for p in output_dir.glob("*.csv") if p.is_file() and date_check in str(p)][0]


def get_rosamond_data(
    acq_date: PreciseDateTime,
    coords_type: CornerReflectorCoordinatesType = CornerReflectorCoordinatesType.INSTANTANEOUS_CRUST,
) -> pd.DataFrame:
    """Get Rosamond Corner Reflector data at a given date as a pandas dataframe.

    Parameters
    ----------
    acq_date : PreciseDateTime
        selected date at which query the data
    coords_type : CornerReflectorCoordinatesType, optional
        selected type of coordinates to be downloaded, by default CornerReflectorCoordinatesType.INSTANTANEOUS_CRUST

    Returns
    -------
    pd.DataFrame
        sct compliant calibration site dataframe
    """
    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        file = download_rosamond_corner_reflector_data(
            output_dir=temp_dir, acquisition_time=acq_date, coords_type=coords_type
        )
        data_df = pd.read_csv(file)

    return convert_rosamund_file_to_compliant_csv(df=data_df.copy(), measurement_date=acq_date)
