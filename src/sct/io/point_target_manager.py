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

from sct.resources import csv_template


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
    if not source.exists():
        raise FileNotFoundError(f"Input file {source} does not exist")
    if source.name.endswith(".csv"):
        # external format, .csv template compliant
        point_targets_df = read_csv_point_targets_file(source=source)
    elif source.name.endswith("json"):
        ...
    else:
        raise UnsupportedPointTargetSource(f"Invalid source file: {source}")

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


def read_geojson_point_targets_file(surveys: Path, product_date: PreciseDateTime | None = None) -> pd.DataFrame:
    """Reading the input .geojson file containing Point Target locations and info and converting it to Pandas DataFrame.

    Parameters
    ----------
    surveys : Path
        path to the surveys .json file
    product_date : PreciseDateTime | None
        product acquisition date, this date is needed to select the proper survey data in case several surveys are
        available, if None, the latest survey is selected, by default None

    Returns
    -------
    pd.DataFrame
        Point Targets DataFrame
    """
    with open(surveys, "r") as f_in:
        survey_data = json.load(f_in)
    survey_data = survey_data["features"]
    df = pd.read_csv(csv_template)
    rows = [dict.fromkeys(df.columns) for _ in range(len(survey_data))]
    for pt_id, pt in enumerate(survey_data):
        pt = survey_data[pt_id]
        date = [int(d) for d in pt["properties"]["survey_date"].split("-")]
        rows[pt_id]["target_name"] = pt["properties"]["target_id"]
        rows[pt_id]["longitude_deg"] = pt["properties"]["lat"]
        rows[pt_id]["latitude_deg"] = pt["properties"]["lon"]
        rows[pt_id]["altitude_m"] = pt["properties"]["elevation"]
        rows[pt_id]["target_type"] = "CR"
        rows[pt_id]["description"] = pt["properties"]["site_name"]
        rows[pt_id]["corner_azimuth_deg"] = pt["properties"]["azimuth_angle"]
        rows[pt_id]["corner_elevation_deg"] = pt["properties"]["boresight_angle"]
        rows[pt_id]["measurement_date"] = PreciseDateTime.from_numeric_datetime(
            year=date[0], month=date[1], day=date[2]
        )
        rows[pt_id]["validity_start_date"] = rows[pt_id]["measurement_date"]
        rows[pt_id]["validity_stop_date"] = PreciseDateTime.from_numeric_datetime(year=2099, month=12, day=31)

    df = pd.DataFrame(rows)

    xyz = llh2xyz(coordinates=df[["longitude_deg", "latitude_deg", "altitude_m"]].to_numpy(dtype=float).T).T
    df["x_coord_m"] = xyz[:, 0]
    df["y_coord_m"] = xyz[:, 1]
    df["z_coord_m"] = xyz[:, 2]

    if product_date is not None:
        # taking the latest measurement date before the product date
        df = df.loc[df["measurement_date"] <= product_date]
        df = df.loc[df.groupby("target_name")["measurement_date"].idxmax()]
    else:
        # taking the latest measurement date
        df = df.loc[df.groupby("target_name")["measurement_date"].idxmax()]

    return df.sort_values("target_name").reset_index(drop=True)


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

    out_df = pd.read_csv(csv_template)

    if not isinstance(df, pd.DataFrame):
        df = pd.read_csv(Path(df))

    # cleaning dataframe
    col_clean = [d.strip().replace('"', "") for d in df.columns]
    df.columns = col_clean
    df.drop(list(df.filter(regex="Epoch")), axis=1, inplace=True)

    out_df = out_df.loc[out_df.index.repeat(len(df))]
    out_df["description"] = "Rosamond Corner Reflector Array (RCRA), Rosamond Dry Lakebed, California, USA"
    out_df["target_name"] = df["Corner ID"].apply(lambda x: "ROS" + f"{x:02d}" + "CR").to_list()
    out_df["latitude_deg"] = df["Latitude (deg)"].to_list()
    out_df["longitude_deg"] = df["Longitude (deg)"].to_list()
    out_df["altitude_m"] = df["Height Above Ellipsoid (m)"].to_list()
    # correcting corner_azimuth_deg to express it with respect to North and not East
    out_df["corner_azimuth_deg"] = (df["Azimuth (deg)"].to_numpy() + 90) % 360
    # correcting corner_elevation_deg to express it with respect to the corner max pointing angle and not to the earth
    # surface, for trihedral corner reflectors
    out_df["corner_elevation_deg"] = df["Tilt / Elevation angle (deg)"].to_numpy() + 35.2644
    out_df["target_size_m"] = df["Side Length (m)"].to_list()

    # creating dummy RCS info for the corner reflectors
    out_df["target_shape"] = "trihedral"
    out_df["rcs_hh_dB"] = 0
    out_df["rcs_hv_dB"] = 0
    out_df["rcs_vv_dB"] = 0
    out_df["rcs_vh_dB"] = 0
    out_df["delay_s"] = 0

    # computing XYZ ECEF coordinates
    lat_lon = np.deg2rad(out_df[["latitude_deg", "longitude_deg"]])
    lat_lon_h = np.c_[lat_lon, out_df["altitude_m"]]
    xyz_coords = llh2xyz(lat_lon_h.T).T

    # adding columns
    out_df["target_type"] = "CR"
    out_df["plate"] = "NOAM"
    out_df["x_coord_m"] = xyz_coords[:, 0]
    out_df["y_coord_m"] = xyz_coords[:, 1]
    out_df["z_coord_m"] = xyz_coords[:, 2]
    out_df["drift_velocity_x_my"] = np.nan
    out_df["drift_velocity_y_my"] = np.nan
    out_df["drift_velocity_z_my"] = np.nan
    out_df["measurement_date"] = measurement_date
    out_df["validity_start_date"] = measurement_date - 24 * 3600  # a day before
    out_df["validity_stop_date"] = measurement_date + 24 * 3600  # a day after

    return out_df
