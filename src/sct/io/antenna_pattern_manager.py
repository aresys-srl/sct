# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Antenna Pattern Data reader
---------------------------
"""

from __future__ import annotations

from pathlib import Path

import xarray as xr
from netCDF4 import Dataset


def read_antenna_pattern_netcdf(path: Path) -> dict[str, dict[str, xr.Dataset]]:
    """Reading Antenna Pattern data from NetCDF file and returning a dictionary containing the content divided by
    swath and polarization.

    Hierarchy:

        root/
        └── swath
            └── direction (e.g. `TW`)
                └──polarization (e.g. `HH`, `VV`)
                    ├── gain (in dB)
                    ├── phase (optional, in rad)
                    ├── azimuth_angles (in deg)
                    └── elevation_angles (in deg)

    !!! note "Supported Products"

        Only Two Way Antenna Patterns are supported, so only one direction group is expected.

    Parameters
    ----------
    path : Path
        Path to the NetCDF file containing the antenna pattern data. The structure of the file must adhere to the
        following structure:

    Returns
    -------
    dict[str, dict[str, xr.Dataset]]
        nested dictionary containing the antenna pattern data divided by swath and polarization
    """
    am_ds = Dataset(path, mode="r")
    antenna_pattern_datasets = {}
    for swath, direction_groups in am_ds.groups.items():
        antenna_pattern_datasets[swath] = {}
        assert len(direction_groups.groups) == 1
        dir_group = direction_groups.groups[list(direction_groups.groups.keys())[0]]
        for pol, pol_group in dir_group.groups.items():
            ds = xr.Dataset(
                {
                    "gain": (
                        ["azimuth_angles", "elevation_angles"],
                        pol_group["gain"][:].data,
                    ),
                },
                coords={
                    "azimuth_angles": pol_group["azimuth_angles"][:].data,
                    "elevation_angles": pol_group["elevation_angles"][:].data,
                },
            )
            ds["gain"].attrs["units"] = pol_group["gain"].units
            ds["azimuth_angles"].attrs["units"] = pol_group["azimuth_angles"].units
            ds["elevation_angles"].attrs["units"] = pol_group["elevation_angles"].units
            antenna_pattern_datasets[swath][pol] = ds
    return antenna_pattern_datasets
