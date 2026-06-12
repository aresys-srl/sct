"""Testing troposphere downloader helper functions"""

from perseo_core.timing import PreciseDateTime
from perseo_perturbations.atmospheric.troposphere import TroposphericGRIDResolution

from sct.web_scraping.troposphere_maps_downloader import _generate_download_link_vmf


def test_generate_download_link_vmf():
    acq_time = PreciseDateTime.from_numeric_datetime(2024, 6, 1, 12, 0, 0)
    map_name = "VMF3_20240601.H00"
    result = _generate_download_link_vmf(acq_time, map_name)
    assert result.startswith("https://vmf.geo.tuwien.ac.at/trop_products/")
    assert "GRID" in result
    assert "1x1" in result
    assert "VMF3" in result
    assert "2024" in result
    assert map_name in result


def test_generate_download_link_vmf_coarse():
    acq_time = PreciseDateTime.from_numeric_datetime(2024, 6, 1, 12, 0, 0)
    map_name = "VMF3_20240601.H00"
    result = _generate_download_link_vmf(acq_time, map_name, TroposphericGRIDResolution.COARSE)
    assert "5x5" in result


def test_generate_download_link_vmf_different_year():
    acq_time = PreciseDateTime.from_numeric_datetime(2023, 1, 15, 0, 0, 0)
    map_name = "VMF3_20230115.H00"
    result = _generate_download_link_vmf(acq_time, map_name)
    assert "2023" in result
