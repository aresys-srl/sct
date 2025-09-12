# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target and Calibration Sites utilities
--------------------------------------------
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from arepytools.geometry.conversions import llh2xyz
from arepytools.timing.precisedatetime import PreciseDateTime
from perseo_quality.io.point_targets import PointTarget


class UnsupportedPointTargetSource(RuntimeError):
    """External point target source provided is not supported"""


def extract_point_target_data_from_source(source: str | Path) -> pd.DataFrame:
    """Managing external point target data source based on its type, unifying the output to the SCT standard.

    Parameters
    ----------
    source : str | Path
        Path to the external source of point target files

    Returns
    -------
    pd.DataFrame
        pandas dataframe corresponding to the input point target file
    """
    source = Path(source)
    if str(source).endswith(".csv"):
        # external format, .csv template compliant
        point_targets_df = pd.read_csv(source)
        for date_in in ("measurement_date", "validity_start_date", "validity_stop_date"):
            if not point_targets_df["measurement_date"].isnull().all():
                point_targets_df[date_in] = pd.to_datetime(point_targets_df[date_in], format="mixed")
                point_targets_df[date_in] = point_targets_df[date_in].apply(
                    lambda x: PreciseDateTime.fromisoformat(x.isoformat()) if not pd.isnull(x) else x
                )
    else:
        raise UnsupportedPointTargetSource(source)

    return point_targets_df


def convert_df_to_nominal_point_target(data_df: pd.DataFrame) -> list[PointTarget]:
    """Convert dataframe to dictionary of NominalPointTarget values.

    Parameters
    ----------
    data_df : pd.DataFrame
        point target dataframe

    Returns
    -------
    list[PointTarget]
        list of Point Target objects
    """
    pt_data = []
    for _, row in data_df.iterrows():
        pt_data.append(
            PointTarget(
                name=row["target_name"],
                xyz_coordinates=row[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy(dtype=float),
                delay=row["delay_s"] if not np.isnan(row["delay_s"]) else None,
                rcs_hh=row["rcs_hh_dB"],
                rcs_hv=row["rcs_hv_dB"],
                rcs_vh=row["rcs_vh_dB"],
                rcs_vv=row["rcs_vv_dB"],
            )
        )

    return pt_data


def convert_rosamond_file_to_compliant_csv(
    df: str | Path | pd.DataFrame, measurement_date: PreciseDateTime
) -> pd.DataFrame:
    """Formatting downloaded Rosamond Point Target Dataset to be compliant with the SCT input .csv format.

    Parameters
    ----------
    df : str | Path | pd.DataFrame
        downloaded Rosamond Point Target dataset, can be a path to the .csv file or the corresponding pandas dataframe
    measurement_date : PreciseDateTime
        measurement date of the current dataset

    Returns
    -------
    pd.DataFrame
        SCT compliant Rosamond dataframe
    """

    if not isinstance(df, pd.DataFrame):
        df = pd.read_csv(Path(df))

    # cleaning dataframe
    col_clean = [d.strip().replace('"', "") for d in df.columns]
    df.columns = col_clean
    df.drop(list(df.filter(regex="Epoch")), axis=1, inplace=True)

    # formatting names
    df.rename(
        columns={
            "Corner ID": "target_name",
            "Latitude (deg)": "latitude_deg",
            "Longitude (deg)": "longitude_deg",
            "Height Above Ellipsoid (m)": "altitude_m",
            "Azimuth (deg)": "corner_azimuth_deg",
            "Tilt / Elevation angle (deg)": "corner_elevation_deg",
            "Side Length (m)": "target_size_m",
        },
        inplace=True,
    )

    # correcting corner_azimuth_deg to express it with respect to North and not East
    df["corner_azimuth_deg"] = (df["corner_azimuth_deg"] + 90) % 360

    # correcting corner_elevation_deg to express it with respect to the corner max pointing angle and not to the earth
    # surface
    df["corner_elevation_deg"] += 35.2644  # for trihedral corner reflectors

    # composing target names
    df["target_name"] = df["target_name"].apply(lambda x: "ROS" + f"{x:02d}" + "CR")

    # creating dummy RCS info for the corner reflectors
    df["target_shape"] = "trihedral"
    df["rcs_hh_dB"] = 0
    df["rcs_hv_dB"] = 0
    df["rcs_vv_dB"] = 0
    df["rcs_vh_dB"] = 0
    df["delay_s"] = 0

    # computing XYZ ECEF coordinates
    lat_lon = np.deg2rad(df[["latitude_deg", "longitude_deg"]])
    lat_lon_h = np.c_[lat_lon, df["altitude_m"]]
    xyz_coords = llh2xyz(lat_lon_h.T).T

    # adding columns
    df["target_type"] = "CR"
    df["plate"] = "NOAM"
    df["x_coord_m"] = xyz_coords[:, 0]
    df["y_coord_m"] = xyz_coords[:, 1]
    df["z_coord_m"] = xyz_coords[:, 2]
    df["drift_velocity_x_my"] = np.nan
    df["drift_velocity_y_my"] = np.nan
    df["drift_velocity_z_my"] = np.nan
    df["measurement_date"] = measurement_date
    df["validity_start_date"] = measurement_date - 24 * 3600  # a day before
    df["validity_stop_date"] = measurement_date + 24 * 3600  # a day after

    return df
