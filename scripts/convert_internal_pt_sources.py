# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Converting Aresys internal Point Target sources (.xml and Binary Folder) to SCT compliant .csv"""

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from arepytools.geometry.conversions import llh2xyz, xyz2llh
from arepytools.io import PointSetProduct, read_point_targets_file
from perseo_quality.core.signal_processing import convert_to_db

from sct.resources import csv_template
from sct.io.point_target_manager import extract_point_target_data_from_source


def convert_point_target_binary_to_df(source: str | Path) -> pd.DataFrame:
    """Convert Aresys Point Target Binary product to SCT internal point target dataframe format.

    Parameters
    ----------
    source : str | Path
        Path to Point Target Binary product

    Returns
    -------
    pd.DataFrame
        SCT compliant internal point target dataframe
    """
    coords, rcs = PointSetProduct(path=source).read_data()
    num = len(coords)
    dummy_data = [None] * len(coords)
    llh_coords = xyz2llh(coords.T).T
    point_targets_df = pd.read_csv(csv_template)
    point_targets_df = point_targets_df.loc[point_targets_df.index.repeat(num)]
    point_targets_df["latitude_deg"] = np.rad2deg(llh_coords[:, 0])
    point_targets_df["longitude_deg"] = np.rad2deg(llh_coords[:, 1])
    point_targets_df["altitude_m"] = llh_coords[:, 2]
    point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = coords
    point_targets_df["target_type"] = "CR"
    point_targets_df["target_name"] = [
        item + "_" + f"{indx + 1:02}" for indx, item in enumerate(point_targets_df["target_type"])
    ]
    point_targets_df["plate"] = dummy_data
    point_targets_df["delay_s"] = 0
    point_targets_df["measurement_date"] = dummy_data
    point_targets_df["validity_start_date"] = dummy_data
    point_targets_df["validity_stop_date"] = dummy_data
    point_targets_df["rcs_hh_dB"] = convert_to_db(np.abs(rcs[:, 0]))
    point_targets_df["rcs_hv_dB"] = convert_to_db(np.abs(rcs[:, 1]))
    point_targets_df["rcs_vh_dB"] = convert_to_db(np.abs(rcs[:, 2]))
    point_targets_df["rcs_vv_dB"] = convert_to_db(np.abs(rcs[:, 3]))

    return point_targets_df


def convert_point_target_file_xml_to_df(source: str | Path) -> pd.DataFrame:
    """Convert Aresys Point Target File XML product to SCT internal point target dataframe format.

    Parameters
    ----------
    source : str | Path
        Path to Point Target File XML product

    Returns
    -------
    pd.DataFrame
        SCT compliant internal point target dataframe
    """
    point_targets = read_point_targets_file(xml_file=source)
    coords = np.stack([c.xyz_coordinates for c in point_targets.values()])
    rcs_hh = np.array([c.rcs_hh for c in point_targets.values()])
    rcs_hv = np.array([c.rcs_hv for c in point_targets.values()])
    rcs_vh = np.array([c.rcs_vh for c in point_targets.values()])
    rcs_vv = np.array([c.rcs_vv for c in point_targets.values()])
    delays = [c.delay for c in point_targets.values()]
    llh_coords = xyz2llh(coords.T).T
    df = pd.read_csv(csv_template)
    df = df.loc[df.index.repeat(len(coords))]
    df["target_name"] = ["cr_" + f"{int(k):02}" for k in list(point_targets.keys())]
    df = df.assign(
        target_type="CR",
        plate="NONE",
        description="None",
        latitude_deg=np.rad2deg(llh_coords[:, 0]),
        longitude_deg=np.rad2deg(llh_coords[:, 1]),
        altitude_m=llh_coords[:, 2],
        x_coord_m=coords[:, 0],
        y_coord_m=coords[:, 1],
        z_coord_m=coords[:, 2],
        drift_velocity_x_my=np.nan,
        drift_velocity_y_my=np.nan,
        drift_velocity_z_my=np.nan,
        delay_s=delays,
        measurement_date=None,
        validity_start_date=None,
        validity_stop_date=None,
        rcs_hh_dB=convert_to_db(np.abs(rcs_hh)),
        rcs_hv_dB=convert_to_db(np.abs(rcs_hv)),
        rcs_vh_dB=convert_to_db(np.abs(rcs_vh)),
        rcs_vv_dB=convert_to_db(np.abs(rcs_vv)),
    )
    return df


def convert_aresys_point_target_formats(source: str | Path) -> pd.DataFrame:
    source = Path(source)
    if str(source).endswith(".xml"):
        # internal format, point target xml file
        point_targets_df = convert_point_target_file_xml_to_df(source=source)
    elif source.is_dir():
        # internal format, point target binary
        point_targets_df = convert_point_target_binary_to_df(source=source)

    return point_targets_df


def convert_csv_point_target_to_geojson(source: str | Path, output_dir: str | Path) -> Path:
    source = Path(source)
    assert source.name.endswith(".csv")
    output_dir = Path(output_dir)
    df = extract_point_target_data_from_source(source=source)
    out = {"type": "FeatureCollection", "features": []}
    for _, row in df.iterrows():
        properties = row[
            [
                "target_name",
                "target_type",
                "plate",
                "description",
                "drift_velocity_x_my",
                "drift_velocity_y_my",
                "drift_velocity_z_my",
                "corner_azimuth_deg",
                "corner_elevation_deg",
                "target_shape",
                "target_size_m",
                "rcs_hh_dB",
                "rcs_hv_dB",
                "rcs_vh_dB",
                "rcs_vv_dB",
                "delay_s",
            ]
        ].to_dict()
        properties["measurement_date"] = datetime.fromisoformat(row["measurement_date"].isoformat()).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        properties["validity_start_date"] = datetime.fromisoformat(row["validity_start_date"].isoformat()).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        properties["validity_stop_date"] = datetime.fromisoformat(row["validity_stop_date"].isoformat()).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )
        out["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "coordinates": row[["longitude_deg", "latitude_deg", "altitude_m"]].to_list(),
                    "type": "Point",
                },
                "properties": properties,
            },
        )
    output_file = output_dir.joinpath(source.name.replace(".csv", ".geojson"))
    with open(output_file, "w") as f_out:
        json.dump(out, f_out, indent=4)
    return output_file


def convert_lat_lon_dataset_to_df(
    coords: np.ndarray,
    rcs: np.ndarray,
    delays: np.ndarray,
    names: list[str],
    target_type: str = "CR",
    plate: str = "EURA",
) -> pd.DataFrame:
    """Convert lat lon dataset to SCT compliant internal point target dataframe format."""

    num = coords.shape[0]
    assert coords.shape[1] == 3
    assert len(names) == coords.shape[0]

    dummy_data = [None] * len(coords)
    coords_ = coords.copy()
    coords_[:, :2] = np.deg2rad(coords[:, :2])
    xyz_coords = llh2xyz(coords_.T).T
    point_targets_df = pd.read_csv(csv_template)
    point_targets_df = point_targets_df.loc[point_targets_df.index.repeat(num)]
    point_targets_df[["latitude_deg", "longitude_deg", "altitude_m"]] = coords
    point_targets_df[["x_coord_m", "y_coord_m", "z_coord_m"]] = xyz_coords
    point_targets_df["target_type"] = target_type
    point_targets_df["target_name"] = names
    point_targets_df["plate"] = plate
    point_targets_df["delay_s"] = delays if delays is not None else np.zeros(num)
    point_targets_df["measurement_date"] = dummy_data
    point_targets_df["validity_start_date"] = dummy_data
    point_targets_df["validity_stop_date"] = dummy_data
    point_targets_df["rcs_hh_dB"] = convert_to_db(np.abs(rcs[:, 0]))
    point_targets_df["rcs_hv_dB"] = convert_to_db(np.abs(rcs[:, 1]))
    point_targets_df["rcs_vh_dB"] = convert_to_db(np.abs(rcs[:, 2]))
    point_targets_df["rcs_vv_dB"] = convert_to_db(np.abs(rcs[:, 3]))

    return point_targets_df


if __name__ == "__main__":
    # pt_path = r"..."
    # output_csv_folder = r"..."
    # df = convert_aresys_point_target_formats(source=pt_path)
    # df.to_csv(Path(output_csv_folder).joinpath("point_targets_dataset.csv"), index=False)

    # convert_csv_point_target_to_geojson(
    #     source=r"C:\ARESYS_PROJ\sct\corner_reflectors_datasets\surat_basin_corner_reflectors_data.csv",
    #     output_dir=r"C:\ARESYS_PROJ\sct\corner_reflectors_datasets",
    # )
    target_df = convert_lat_lon_dataset_to_df(
        coords=np.array(
            [
                [48.02993879, 9.81195953, 704.7],
                [48.06801023, 9.91851521, 667.1],
                [48.06736819, 10.08008266, 606.1],
                [48.07005964, 10.43542688, 643.4],
                [48.04666707, 10.58140924, 649.6],
                [48.06454864, 10.92642479, 661.3],
            ]
        ),
        rcs=np.array(
            [
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
            ]
        ),
        delays=np.zeros(6),
        names=["D38", "D39", "D40", "D41", "D42", "D43"],
        target_type="TX",
    )
    target_df.to_csv("point_targets_dataset.csv", index=False)
