# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target and Calibration Sites utilities
--------------------------------------------
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from arepytools.geometry.conversions import llh2xyz
from arepytools.timing.precisedatetime import PreciseDateTime
from perseo_quality.io.point_targets import PointTarget

from sct import csv_template


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
    if source.name.endswith(".csv"):
        # external format, .csv template compliant
        point_targets_df = read_csv_point_targets_file(source=source)
    elif source.name.endswith(".geojson"):
        ...
    else:
        raise UnsupportedPointTargetSource(source)

    return point_targets_df


def read_csv_point_targets_file(source: Path) -> pd.DataFrame:
    """Reading the input .csv file containing Point Target locations and info and converting it to a Pandas DataFrame.

    Parameters
    ----------
    source : Path
        path to the .csv file

    Returns
    -------
    pd.DataFrame
        Point Targets DataFrame
    """
    df = pd.read_csv(source)
    for date_in in ("measurement_date", "validity_start_date", "validity_stop_date"):
        if not df["measurement_date"].isnull().all():
            df[date_in] = pd.to_datetime(df[date_in], format="mixed")
            df[date_in] = df[date_in].apply(
                lambda x: PreciseDateTime.fromisoformat(x.isoformat()) if not pd.isnull(x) else x
            )
    return df


def read_geojson_point_targets_file(source: Path) -> pd.DataFrame:
    """Reading the input .geojson file containing Point Target locations and info and converting it to Pandas DataFrame.

    Parameters
    ----------
    source : Path
        path to the .geojson file

    Returns
    -------
    pd.DataFrame
        Point Targets DataFrame
    """
    with open(source, "r") as f_in:
        data = json.load(f_in)
    data = data["features"]
    df = pd.read_csv(csv_template)
    rows = [dict.fromkeys(df.columns) for _ in range(len(data))]
    for pt_id, pt in enumerate(data):
        pt = data[pt_id]
        rows[pt_id]["longitude_deg"] = pt["geometry"]["coordinates"][0]
        rows[pt_id]["latitude_deg"] = pt["geometry"]["coordinates"][1]
        try:
            rows[pt_id]["altitude_m"] = pt["geometry"]["coordinates"][2]
        except IndexError:
            rows[pt_id]["altitude_m"] = 0
        xyz = llh2xyz(
            coordinates=np.deg2rad(
                [rows[pt_id]["latitude_deg"], rows[pt_id]["longitude_deg"], rows[pt_id]["altitude_m"]]
            )
        ).squeeze()
        rows[pt_id]["x_coord_m"], rows[pt_id]["y_coord_m"], rows[pt_id]["z_coord_m"] = xyz

        for prop in pt["properties"]:
            if prop in df.columns:
                if "date" in prop:
                    rows[pt_id][prop] = PreciseDateTime.from_utc_string(pt["properties"][prop])
                else:
                    rows[pt_id][prop] = pt["properties"][prop]

    return pd.DataFrame(rows)


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


if __name__ == "__main__":
    read_geojson_point_targets_file(
        r"C:\ARESYS_PROJ\sct\corner_reflectors_datasets\surat_basin_corner_reflectors_data.geojson"
    )
