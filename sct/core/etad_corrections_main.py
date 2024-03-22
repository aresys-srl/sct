# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Loading of ETAD corrections
---------------------------
"""

import warnings
from pathlib import Path
from typing import Union

import pandas as pd
from s1etad import ECorrectionType, Sentinel1Etad, Sentinel1EtadBurst
from scipy.interpolate import interp2d
from shapely.errors import ShapelyDeprecationWarning
from shapely.geometry import Point

# due to s1etad use of deprecated shapely function
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)


def _extract_etad_correction(burst: Sentinel1EtadBurst, location: Point) -> tuple[float, float]:
    """Extracting ALE range correction from ETAD product for a given point target location.

    Parameters
    ----------
    burst : Sentinel1EtadBurst
        burst where the target lies
    location : Point
        location of the target

    Returns
    -------
    float
        range ALE correction in meters
    """
    # get SAR times at which it is seen in the scene
    tau0, t0 = burst.geodetic_to_radar(location.y, location.x, location.z)
    # retrieving sum of all corrections along range direction
    correction = burst.get_correction(ECorrectionType.SUM, meter=True)
    rng_corrections = correction["x"]
    az_corrections = correction["y"]

    # interpolating values at given target time coordinates
    azimuth_time, range_time = burst.get_burst_grid()
    interpolator_rng = interp2d(range_time, azimuth_time, rng_corrections)
    interpolator_az = interp2d(range_time, azimuth_time, az_corrections)

    return interpolator_rng(tau0, t0)[0], interpolator_az(tau0, t0)[0]


def get_etad_corrections(etad_product_path: Union[str, Path], target_df: pd.DataFrame) -> pd.DataFrame:
    """Retrieving range ALE correction from ETAD product for all point targets.

    Parameters
    ----------
    etad_product_path : Union[str, Path]
        path to the ETAD product
    target_df : pd.DataFrame
        point target data frame

    Returns
    -------
    pd.DataFrame
        corrections dataframe
    """

    # opening ETAD product
    etad = Sentinel1Etad(etad_product_path)

    corrections = []
    for _, row in target_df.iterrows():
        # creating a Point instance for the current cor
        cr_point = Point(row["longitude_deg"], row["latitude_deg"], row["altitude_m"])
        cr_burst_location = etad.query_burst(geometry=cr_point)
        if cr_burst_location.empty:
            continue

        total_rng_correction, total_az_correction = _extract_etad_correction(
            burst=next(etad.iter_bursts(cr_burst_location)), location=cr_point
        )

        corrections.append(
            {
                "target_name": row["target_name"],
                "etad_range_correction_[m]": total_rng_correction,
                "etad_azimuth_correction_[m]": total_az_correction,
            }
        )

    return pd.DataFrame(corrections)
