# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Converting Aresys internal Point Target sources (.xml and Binary Folder) to SCT compliant .csv"""

from pathlib import Path

import numpy as np
import pandas as pd
from arepytools.geometry.conversions import xyz2llh
from arepytools.io import PointSetProduct, read_point_targets_file
from arepytools.timing.precisedatetime import PreciseDateTime
from perseo_quality.core.signal_processing import convert_to_db

from sct import csv_template


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


if __name__ == "__main__":
    pt_path = r"..."
    output_csv_folder = r"..."
    df = convert_aresys_point_target_formats(source=pt_path)
    df.to_csv(Path(output_csv_folder).joinpath("point_targets_dataset.csv"), index=False)
