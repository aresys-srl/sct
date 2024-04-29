# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target and Calibration Sites utilities
--------------------------------------------
"""

from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from arepytools.geometry.conversions import llh2xyz
from arepytools.io import PointSetProduct, read_point_targets_file
from arepytools.io.io_support import NominalPointTarget
from arepytools.timing.precisedatetime import PreciseDateTime

from sct import csv_template


class UnsupportedPointTargetSource(RuntimeError):
    """External point target source provided is not supported"""


def extract_point_target_data_from_source(source: Union[str, Path]) -> pd.DataFrame:
    """Managing external point target data source based on its type, unifying the output to the SCT standard.

    Parameters
    ----------
    source : Union[str, Path]
        Path to the external source of point target files

    Returns
    -------
    pd.DataFrame
        pandas dataframe corresponding to the input point target file
    """
    source = Path(source)

    if str(source).endswith(".xml"):
        # internal format, point target xml file
        point_targets_df = convert_point_target_file_xml_to_df(source=source)
    elif source.is_dir():
        # internal format, point target binary
        point_targets_df = convert_point_target_binary_to_df(source=source)

    elif str(source).endswith(".csv"):
        # external format, .csv template compliant
        point_targets_df = pd.read_csv(source)
        for date_in in ("measurement_date", "validity_start_date", "validity_stop_date"):
            if not point_targets_df["measurement_date"].isnull().all():
                point_targets_df[date_in] = pd.to_datetime(point_targets_df[date_in])
                point_targets_df[date_in] = point_targets_df[date_in].apply(
                    lambda x: PreciseDateTime.fromisoformat(x.isoformat()) if not pd.isnull(x) else x
                )
    else:
        raise UnsupportedPointTargetSource(source)

    return point_targets_df


def convert_point_target_binary_to_df(source: Union[str, Path]) -> pd.DataFrame:
    """Convert Aresys Point Target Binary product to SCT internal point target dataframe format.

    Parameters
    ----------
    source : Union[str, Path]
        Path to Point Target Binary product

    Returns
    -------
    pd.DataFrame
        SCT compliant internal point target dataframe
    """
    coords, _ = PointSetProduct(path=source).read_data()
    num = len(coords)
    dummy_data = [None] * len(coords)
    point_targets_df = pd.read_csv(csv_template)
    point_targets_df = point_targets_df.loc[point_targets_df.index.repeat(num)]
    point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = coords
    point_targets_df["target_type"] = "CR"
    point_targets_df["target_name"] = [
        item + "_" + f"{indx+1:02}" for indx, item in enumerate(point_targets_df["target_type"])
    ]
    point_targets_df["plate"] = dummy_data
    point_targets_df["delay_s"] = 0
    point_targets_df["measurement_date"] = dummy_data
    point_targets_df["validity_start_date"] = dummy_data
    point_targets_df["validity_stop_date"] = dummy_data

    return point_targets_df


def convert_point_target_file_xml_to_df(source: Union[str, Path]) -> pd.DataFrame:
    """Convert Aresys Point Target File XML product to SCT internal point target dataframe format.

    Parameters
    ----------
    source : Union[str, Path]
        Path to Point Target File XML product

    Returns
    -------
    pd.DataFrame
        SCT compliant internal point target dataframe
    """
    point_targets = read_point_targets_file(xml_file=source)
    coords = np.stack([c.xyz_coordinates for c in point_targets.values()])
    delays = [c.delay for c in point_targets.values()]
    df = pd.DataFrame(["cr_" + f"{int(k):02}" for k in list(point_targets.keys())], columns=["target_name"])
    df = df.assign(
        target_type="CR",
        plate="NONE",
        x_coord_m=coords[:, 0],
        y_coord_m=coords[:, 1],
        z_coord_m=coords[:, 2],
        drift_velocity_x_my=np.nan,
        drift_velocity_y_my=np.nan,
        drift_velocity_z_my=np.nan,
        delay_s=delays,
        measurement_date=PreciseDateTime(),
        validity_start_date=PreciseDateTime(),
        validity_stop_date=PreciseDateTime.from_numeric_datetime(3000),
    )
    return df


def convert_df_to_nominal_point_target(data_df: pd.DataFrame) -> dict[str, NominalPointTarget]:
    """Convert dataframe to dictionary of NominalPointTarget values.

    Parameters
    ----------
    data_df : pd.DataFrame
        point target dataframe

    Returns
    -------
    dict[str, NominalPointTarget]
        dictionary with keys being point target ids and values being NominalPointTarget dataclasses
    """
    data_dict = dict.fromkeys(data_df.target_name)
    for _, row in data_df.iterrows():
        delay = row["delay_s"] if not np.isnan(row["delay_s"]) else None
        data_dict[row["target_name"]] = NominalPointTarget(
            xyz_coordinates=row[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy(dtype=float),
            delay=delay,
            rcs_hh=row["rcs_hh_dB"],
            rcs_hv=row["rcs_hv_dB"],
            rcs_vh=row["rcs_vh_dB"],
            rcs_vv=row["rcs_vv_dB"],
        )

    return data_dict


def convert_rosamund_file_to_compliant_csv(
    df: Union[str, Path, pd.DataFrame], measurement_date: PreciseDateTime
) -> pd.DataFrame:
    """Formatting downloaded Rosamond Point Target Dataset to be compliant with the SCT input .csv format.

    Parameters
    ----------
    df : Union[str, Path, pd.DataFrame]
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
            "Side Length (m)": "side_length_m",
        },
        inplace=True,
    )

    # composing target names
    df["target_name"] = df["target_name"].apply(lambda x: "ROS" + f"{x:02d}" + "CR")

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
    df["delay_s"] = 0
    df["measurement_date"] = measurement_date
    df["validity_start_date"] = measurement_date - 24 * 3600  # a day before
    df["validity_stop_date"] = measurement_date + 24 * 3600  # a day after

    return df
