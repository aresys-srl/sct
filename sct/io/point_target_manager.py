# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Point Target and Calibration Sites utilities
--------------------------------------------
"""

import datetime
import sqlite3
from enum import Enum
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from arepytools.io import PointSetProduct, read_point_targets_file
from arepytools.io.io_support import NominalPointTarget
from arepytools.timing.precisedatetime import PreciseDateTime

from sct import calibration_sites_db, csv_template

SELECT_JOIN_QUERY = """
SELECT target_name, target_type.type, plate.plate, reference_frame.reference,
x_coord_m, y_coord_m, z_coord_m, drift_velocity_x_my, drift_velocity_y_my, drift_velocity_z_my,
delay_s, measurement_date, validity_start_date, validity_end_date
FROM XXXX
INNER JOIN target_type ON target_type.ID = XXXX.target_type
INNER JOIN plate ON plate.ID = XXXX.plate
INNER JOIN reference_frame ON reference_frame.ID = XXXX.xyz_reference_frame;
"""

SELECT_JOIN_QUERY_WITH_TIME = """
SELECT target_name, target_type.type, plate.plate, reference_frame.reference,
x_coord_m, y_coord_m, z_coord_m, drift_velocity_x_my, drift_velocity_y_my, drift_velocity_z_my,
delay_s, measurement_date, validity_start_date, validity_end_date
FROM XXXX
WHERE XXXX.validity_start_date <  ?;
"""
# INNER JOIN target_type ON target_type.ID = XXXX.target_type
# INNER JOIN plate ON plate.ID = XXXX.plate
# INNER JOIN reference_frame ON reference_frame.ID = XXXX.xyz_reference_frame;
# """


class UnsupportedPointTargetSource(RuntimeError):
    """External point target source provided is not supported"""


class SupportedCalibrationSites(Enum):
    """Supported Calibration Sites inside internal point target database"""

    SURAT_BASIN = "surat_basin"


def extract_point_target_data_from_source(source: Union[str, Path]) -> pd.DataFrame:
    """Managing external point target data source based on its type, unifying the output to the SCT standard.

    Parameters
    ----------
    source : Union[str, Path]
        Path to the external source of point target files

    Returns
    -------
    pd.DataFrame
        _description_
    """
    source = Path(source)

    if str(source).endswith(".xml"):
        # internal format, point target xml file
        point_targets = read_point_targets_file(xml_file=source)
        raise NotImplementedError
    elif source.is_dir():
        # internal format, point target binary
        point_targets_df = convert_point_target_binary_to_df(source=source)

    elif str(source).endswith(".csv"):
        # external format, .csv template compliant
        point_targets_df = pd.read_csv(source)
        point_targets_df["measurement_date"] = pd.to_datetime(point_targets_df["measurement_date"])
        point_targets_df["validity_start_date"] = pd.to_datetime(point_targets_df["validity_start_date"])
        point_targets_df["validity_stop_date"] = pd.to_datetime(point_targets_df["validity_stop_date"])
    else:
        raise UnsupportedPointTargetSource(source)

    return point_targets_df


def query_calibration_sites_db(
    calibration_site: SupportedCalibrationSites = SupportedCalibrationSites.SURAT_BASIN,
    acquisition_time: PreciseDateTime = None,
) -> pd.DataFrame:
    """Reading calibration sites DB to extract data corresponding to a given site.

    Parameters
    ----------
    calibration_site : SupportedCalibrationSites, optional
        calibration site of interest, by default SupportedCalibrationSites.SURAT_BASIN
    acquisition_time : PreciseDateTime, optional
        if provided, query is restricted only to those target valid at the time of acquisition, by default None

    Returns
    -------
    pd.DataFrame
        dataframe containing point target data extracted from db
    """
    connection = sqlite3.connect(calibration_sites_db)

    data_df = pd.read_sql_query(
        SELECT_JOIN_QUERY.replace("XXXX", calibration_site.value),
        connection,
        parse_dates=["measurement_date", "validity_start_date", "validity_end_date"],
    )

    if acquisition_time is not None:
        acq_date = datetime.datetime(acquisition_time.year, acquisition_time.month, acquisition_time.day_of_the_month)
        data_df = data_df.query("validity_start_date <= @acq_date & validity_end_date >= @acq_date")

    # substituting all None with Nan
    data_df = data_df.fillna(value=np.nan)

    return data_df


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


def convert_df_to_nominal_point_target(data_df: pd.DataFrame) -> dict[str, NominalPointTarget]:
    """Convert dataframe read from database to dictionary of NominalPointTarget values.

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
        data_dict[row["target_name"]] = NominalPointTarget(
            xyz_coordinates=row[["x_coord_m", "y_coord_m", "z_coord_m"]].to_numpy(dtype=float),
            delay=row["delay_s"],
            rcs_hh=1,
            rcs_hv=1,
            rcs_vh=1,
            rcs_vv=1,
        )

    return data_dict
