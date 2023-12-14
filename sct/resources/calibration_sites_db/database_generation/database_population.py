# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Populating point target database"""

import sqlite3
from pathlib import Path
from typing import Union

import pandas as pd

PLATES = ["ANTA", "ARAB", "AUST", "EURA", "INDI", "NAZC", "NOAM", "NUBI", "PCFC", "SOAM", "SOMA"]
REFERENCE_FRAMES = ["ECEF", "GDA2020"]
TARGET_TYPES = ["CR", "TX"]


def populate_plates(cursor: sqlite3.Cursor) -> None:
    """Populating the plate table inside the sqlite database.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        database cursor from active connection
    """
    cursor.executemany("INSERT INTO plate(plate) VALUES(?)", [(p,) for p in PLATES])


def populate_reference_frames(cursor: sqlite3.Cursor) -> None:
    """Populating the reference_frame table inside the sqlite database.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        database cursor from active connection
    """
    cursor.executemany("INSERT INTO reference_frame(reference) VALUES(?)", [(r,) for r in REFERENCE_FRAMES])


def populate_target_types(cursor: sqlite3.Cursor) -> None:
    """Populating the target_type table inside the sqlite database.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        database cursor from active connection
    """
    cursor.executemany("INSERT INTO target_type(type) VALUES(?)", [(t,) for t in TARGET_TYPES])


def populate_surat_basin(cursor: sqlite3.Cursor, data: pd.DataFrame) -> None:
    """Populating the surat_basin table inside the sqlite database.

    Parameters
    ----------
    cursor : sqlite3.Cursor
        database cursor from active connection
    data : pd.DataFrame
        dataframe containing point targets data
    """

    ecef_id = cursor.execute("SELECT ID FROM reference_frame WHERE reference = 'ECEF'").fetchall()[0][0]
    aust_id = cursor.execute("SELECT ID FROM plate WHERE plate = 'AUST'").fetchall()[0][0]
    cr_id = cursor.execute("SELECT ID FROM target_type WHERE type = 'CR'").fetchall()[0][0]
    surat_basin_columns = [p[1] for p in cursor.execute("PRAGMA table_info(surat_basin);").fetchall()]

    insert_string = (
        f"INSERT INTO surat_basin({', '.join(surat_basin_columns[1:])})"
        + f" VALUES({'?, '*(len(surat_basin_columns)-2) + '?'});"
    )

    data_values = []
    for idx, row in data.iterrows():
        # SB01-CRApex like
        target_name = "SB" + f"{idx+1:02d}" + "CRApex"
        data_values.append(
            (
                target_name,
                cr_id,
                aust_id,
                ecef_id,
                row["Description"],
                row["Latitude [deg]"],
                row["Longitude [deg]"],
                row["Altitude [m]"],
                row["x [m]"],
                row["y [m]"],
                row["z [m]"],
                row["vx [m/y]"],
                row["vy [m/y]"],
                row["vz [m/y]"],
                row["Azimuth [deg]"],
                row["Elevation [deg]"],
                row["Delay [s]"],
                row["Survey Time [UTC]"],
                row["Validity Start [UTC]"],
                row["Validity Stop [UTC]"],
            )
        )

    cursor.executemany(insert_string, data_values)


def populate_whole_database(db_path: Union[str, Path], data_dict: dict[str, pd.DataFrame]) -> None:
    """Populating the whole empty point targets sqlite database.

    Parameters
    ----------
    db_path : Union[str, Path]
        Path to the empty database
    data_dict : dict[str, pd.DataFrame]
        dictionary containing data for the point targets
    """
    db = Path(db_path)
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    populate_plates(cursor=cursor)
    connection.commit()
    populate_reference_frames(cursor=cursor)
    connection.commit()
    populate_target_types(cursor=cursor)
    connection.commit()

    if "surat_basin" in data_dict.keys():
        populate_surat_basin(cursor=cursor, data=data_dict["surat_basin"])
        connection.commit()

    connection.close()


if __name__ == "__main__":
    db_file = r"C:\ARESYS_PROJ\sct\calibration_sites_db\calibration_sites.sqlite"
    data_file = r"C:\ARESYS_PROJ\sct\calibration_sites_db\database_generation\surat_basin_data.csv"

    # preparing data
    surat_basin_data = pd.read_csv(data_file)
    data_dict = {"surat_basin": surat_basin_data}

    populate_whole_database(db_path=db_file, data_dict=data_dict)
