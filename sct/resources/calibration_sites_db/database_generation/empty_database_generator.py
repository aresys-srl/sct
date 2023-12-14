# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Creating an empty point target database"""

import sqlite3
from pathlib import Path
from typing import Union

target_type_table = """CREATE TABLE target_type (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	"type" TEXT(4)
);
"""

plate_table = """CREATE TABLE plate (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	plate TEXT(6)
);
"""

reference_frame_table = """CREATE TABLE reference_frame (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	reference TEXT(10)
);
"""

point_target_base_table = """CREATE TABLE XXXXXX (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	target_name TEXT(15),
	target_type INTEGER,
	plate INTEGER,
	xyz_reference_frame INTEGER,
	description TEXT(30),
	latitude_deg NUMERIC,
	longitude_deg NUMERIC,
	altitude_m NUMERIC,
	x_coord_m NUMERIC,
	y_coord_m NUMERIC,
	z_coord_m NUMERIC,
	drift_velocity_x_my NUMERIC,
	drift_velocity_y_my NUMERIC,
	drift_velocity_z_my NUMERIC,
	corner_azimuth_deg NUMERIC,
	corner_elevation_deg NUMERIC,
	delay_s NUMERIC,
	measurement_date TEXT,
	validity_start_date TEXT,
	validity_end_date TEXT,
	FOREIGN KEY(target_type) REFERENCES target_type(ID) ON DELETE SET NULL,
	FOREIGN KEY(plate) REFERENCES plate(ID) ON DELETE SET NULL,
	FOREIGN KEY(xyz_reference_frame) REFERENCES reference_frame(ID) ON DELETE SET NULL
);
"""


def create_empty_database(db_path: Union[str, Path]) -> None:
    """Creating a default empty instance of a SQLite point target database.

    Parameters
    ----------
    db_path : Union[str, Path]
        Path where to write the database
    """
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # creating empty tables
    cur.execute(target_type_table)
    cur.execute(plate_table)
    cur.execute(reference_frame_table)

    # creating surat basin table
    surat_basin_table = point_target_base_table.replace("XXXXXX", "surat_basin")
    cur.execute(surat_basin_table)

    conn.close()


if __name__ == "__main__":
    db_rel_path = r"calibration_sites_db\calibration_sites.sqlite"
    create_empty_database(db_path=db_rel_path)
