# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Troposphere products downloader
-------------------------------
"""

from enum import Enum
from pathlib import Path

import requests
from arepyextras.perturbations.atmospheric.troposphere import (
    TroposphericGRIDResolution,
    TroposphericMapModel,
    TroposphericMapType,
    generate_tropospheric_map_name_for_vmf_data,
)
from arepytools.timing.precisedatetime import PreciseDateTime


class TroposphericWebArchives(Enum):
    """Tropospheric web archives where to download data from"""

    CDDIS = r"https://cddis.nasa.gov/archive/gnss/products/troposphere/zpd"
    VMF = r"https://vmf.geo.tuwien.ac.at/trop_products/"


def _generate_download_link_vmf(
    acq_time: PreciseDateTime,
    map_name: str,
    map_resolution: TroposphericGRIDResolution = TroposphericGRIDResolution.FINE,
) -> str:
    """Generate url to the troposphere products to be downloaded from the VMF archive.

    Parameters
    ----------
    acq_time : PreciseDateTime
        acquisition time
    map_name : str
        name of the product map to be downloaded

    Returns
    -------
    str
        complete url to download the compressed map
    """
    return "/".join(
        [
            TroposphericWebArchives.VMF.value,
            TroposphericMapModel.GRID.name,
            map_resolution.value,
            TroposphericMapType.VMF3.name,
            TroposphericMapType.VMF3.name + "_" + "OP",
            str(acq_time.year),
            map_name,
        ]
    )


def download_tropospheric_products(
    acq_date: PreciseDateTime,
    output_dir: str | Path,
    map_type: TroposphericMapType = TroposphericMapType.VMF3,
    map_grid_resolution: TroposphericGRIDResolution = TroposphericGRIDResolution.FINE,
) -> list[Path]:
    """Fetching the tropospheric products for the input acquisition time from VMF archive.

    Parameters
    ----------
    acq_date : PreciseDateTime
        acquisition date of interest
    output_dir : str | Path
        path to output directory where to save downloaded files
    map_type : TroposphericMapType, optional
        tropospheric product map type, by default TroposphericMapType.VMF3
    map_grid_resolution : TroposphericGRIDResolution, optional
        tropospheric GRID product map resolution, by default TroposphericGRIDResolution.FINE

    Returns
    -------
    Path
        list of downloaded products Paths
    """
    output_dir = Path(output_dir)
    map_names, _ = generate_tropospheric_map_name_for_vmf_data(acq_time=acq_date, map_type=map_type)

    out_files = []
    for file in map_names:
        download_link = _generate_download_link_vmf(
            acq_time=acq_date, map_name=file, map_resolution=map_grid_resolution
        )

        response = requests.get(download_link, allow_redirects=True, timeout=10)

        filename = output_dir.joinpath(file)

        with open(output_dir.joinpath(file), "wb") as f_out:
            f_out.write(response.content)

        out_files.append(filename)

    return out_files


if __name__ == "__main__":
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    date = PreciseDateTime.from_numeric_datetime(2023, 5, 23, 13, 30)
    download_tropospheric_products(acq_date=date, output_dir=out_dir)
