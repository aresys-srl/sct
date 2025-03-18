# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Aresys Product Folder format Arepyextras-Quality protocol-compliant wrapper
---------------------------------------------------------------------------
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Callable

import numpy as np
from arepyextras.quality.io.quality_input_from_product_folder import ProductFolderManager
from arepytools.geometry.conversions import xyz2llh
from arepytools.geometry.direct_geocoding import direct_geocoding_monostatic
from arepytools.io import read_metadata
from arepytools.io.create_orbit import create_orbit
from arepytools.io.productfolder2 import is_product_folder as is_aresys_product
from arepytools.math.genericpoly import create_sorted_poly_list
from shapely import Polygon


class ProductFolderManagerExtended(ProductFolderManager):
    def __init__(self, path: str | Path, **kwargs) -> None:
        super().__init__(path)

    def _compute_footprint(self) -> Polygon:
        """Computing Product Folder scene footprint considering all channels.

        Returns
        -------
        Polygon
            Polygon object corresponding to the Product Folder lat/lon scene footprint
        """
        footprint_corners = []
        for channel_id in self._channel_list:
            metadata = read_metadata(self._product.get_channel_metadata(channel_id))
            dataset_info = metadata.get_dataset_info()
            burst_info = metadata.get_burst_info()
            raster_info = metadata.get_raster_info()
            trajectory = create_orbit(state_vectors=metadata.get_state_vectors())

            if burst_info is not None:
                first_burst = burst_info.get_burst(0)
                last_burst = burst_info.get_burst(burst_info.get_number_of_bursts() - 1)
                corners_az = [
                    last_burst.azimuth_start_time + last_burst.lines * raster_info.lines_step,
                    last_burst.azimuth_start_time + last_burst.lines * raster_info.lines_step,
                    first_burst.azimuth_start_time,
                    first_burst.azimuth_start_time,
                ]
            else:
                corners_az = [
                    raster_info.lines_start + raster_info.lines * raster_info.lines_step,
                    raster_info.lines_start + raster_info.lines * raster_info.lines_step,
                    raster_info.lines_start,
                    raster_info.lines_start,
                ]

            corners_rng = [
                raster_info.samples_start,
                raster_info.samples_start + raster_info.samples * raster_info.samples_step,
                raster_info.samples_start + raster_info.samples * raster_info.samples_step,
                raster_info.samples_start,
            ]
            if dataset_info.projection == "GROUND RANGE":
                gts_poly = metadata.get_ground_to_slant()
                corners_rng = [
                    create_sorted_poly_list(gts_poly).evaluate((raster_info.lines_start, r)) for r in corners_rng
                ]

            for az, rng in zip(corners_az, corners_rng, strict=True):
                corner_xyz = direct_geocoding_monostatic(
                    sensor_positions=trajectory.evaluate(az),
                    sensor_velocities=trajectory.evaluate_first_derivatives(az),
                    range_times=rng,
                    frequencies_doppler_centroid=0,
                    wavelength=1,
                    geodetic_altitude=0,
                    geocoding_side=dataset_info.side_looking.value,
                )
                corner_llh = xyz2llh(corner_xyz).squeeze()
                footprint_corners.append(np.rad2deg(corner_llh[:2]))

        footprint = np.stack(footprint_corners)
        min_lat, min_lon = footprint.min(axis=0)
        max_lat, max_lon = footprint.max(axis=0)
        boundaries = [min_lat, max_lat, min_lon, max_lon]
        region_corners = list(product(boundaries[:2], boundaries[2:]))
        return Polygon(region_corners)

    @property
    def footprint(self) -> Polygon | None:
        """Get product scene footprint as a Shapely Polygon"""
        return self._compute_footprint()


def get_manager() -> type[ProductFolderManagerExtended]:
    """Retrieve manager"""
    return ProductFolderManagerExtended


def get_detector() -> Callable[[str | Path], bool]:
    """Retrieve detector"""
    return is_aresys_product


def get_azimuth_corrections():
    """Retrieve ALE correction function for azimuth direction"""
    return None


def get_range_corrections():
    """Retrieve ALE correction function for range direction"""
    return None
