"""Testing ionosphere TEC map downloader helper functions"""

from arepytools.timing.precisedatetime import PreciseDateTime
from perseo_perturbations.atmospheric.ionosphere import IonosphericAnalysisCenters

from sct.web_scraping.ionosphere_tec_map_downloader import (
    _generate_file_directory_on_server,
    _generate_product_archive_name,
)


def test_generate_file_directory_on_server():
    acq_time = PreciseDateTime.from_numeric_datetime(2024, 6, 1, 12, 0, 0)
    result = _generate_file_directory_on_server(acq_time)
    year = acq_time.year
    doy = acq_time.day_of_the_year
    assert result == f"gnss/products/ionex/{year}/{doy:03d}"


def test_generate_file_directory_on_server_leap_year():
    acq_time = PreciseDateTime.from_numeric_datetime(2024, 12, 31, 0, 0, 0)
    result = _generate_file_directory_on_server(acq_time)
    assert result.endswith("366")


def test_generate_product_archive_name_old_format():
    acq_time = PreciseDateTime.from_numeric_datetime(1999, 6, 1, 12, 0, 0)
    center = IonosphericAnalysisCenters.COD
    result = _generate_product_archive_name(acq_time, center)
    assert result.endswith(".Z")


def test_generate_product_archive_name_new_format():
    acq_time = PreciseDateTime.from_numeric_datetime(2024, 6, 1, 12, 0, 0)
    center = IonosphericAnalysisCenters.COD
    result = _generate_product_archive_name(acq_time, center)
    assert result.endswith(".gz")
