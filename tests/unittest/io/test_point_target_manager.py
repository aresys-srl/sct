"""Testing point target manager"""

import numpy as np
import pandas as pd
import pytest
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.io.point_target_manager import (
    UnsupportedPointTargetSource,
    convert_df_to_nominal_point_target,
    convert_rosamond_file_to_compliant_csv,
    extract_point_target_data_from_source,
    read_csv_point_targets_file,
)


def test_read_csv_point_targets_file(tmp_path):
    csv_content = """target_name,latitude_deg,longitude_deg,altitude_m,target_type,description,corner_azimuth_deg,corner_elevation_deg,target_size_m,measurement_date,validity_start_date,validity_stop_date,delay_s,rcs_hh_dB,rcs_hv_dB,rcs_vh_dB,rcs_vv_dB,plate,x_coord_m,y_coord_m,z_coord_m,drift_velocity_x_my,drift_velocity_y_my,drift_velocity_z_my
T1,45.0,9.0,100.0,CR,test,0.0,35.0,0.7,2024-06-01,2024-06-01,2025-06-01,0.0,0,0,0,0,NOAM,100.0,200.0,300.0,,,
"""  # noqa: E501
    csv_file = tmp_path / "targets.csv"
    csv_file.write_text(csv_content)

    df = read_csv_point_targets_file(csv_file)
    assert len(df) == 1
    assert df.loc[0, "target_name"] == "T1"


def test_read_csv_point_targets_file_nan_dates(tmp_path):
    csv_content = """target_name,latitude_deg,longitude_deg,altitude_m,target_type,description,corner_azimuth_deg,corner_elevation_deg,target_size_m,measurement_date,validity_start_date,validity_stop_date,delay_s,rcs_hh_dB,rcs_hv_dB,rcs_vh_dB,rcs_vv_dB,plate,x_coord_m,y_coord_m,z_coord_m,drift_velocity_x_my,drift_velocity_y_my,drift_velocity_z_my
T1,45.0,9.0,100.0,CR,test,0.0,35.0,0.7,,,2025-06-01,0.0,0,0,0,0,NOAM,100.0,200.0,300.0,,,
"""  # noqa: E501
    csv_file = tmp_path / "targets.csv"
    csv_file.write_text(csv_content)

    df = read_csv_point_targets_file(csv_file)
    assert len(df) == 1


def test_extract_point_target_data_from_source_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_point_target_data_from_source(tmp_path / "nonexistent.csv")


def test_extract_point_target_data_from_source_unsupported(tmp_path):
    unsupported = tmp_path / "targets.xyz"
    unsupported.write_text("")
    with pytest.raises(UnsupportedPointTargetSource):
        extract_point_target_data_from_source(unsupported)


def test_extract_point_target_data_from_source_csv(tmp_path):
    csv_content = """target_name,latitude_deg,longitude_deg,altitude_m,target_type,description,corner_azimuth_deg,corner_elevation_deg,target_size_m,measurement_date,validity_start_date,validity_stop_date,delay_s,rcs_hh_dB,rcs_hv_dB,rcs_vh_dB,rcs_vv_dB,plate,x_coord_m,y_coord_m,z_coord_m,drift_velocity_x_my,drift_velocity_y_my,drift_velocity_z_my
T1,45.0,9.0,100.0,CR,test,0.0,35.0,0.7,2024-06-01,2024-06-01,2025-06-01,0.0,0,0,0,0,NOAM,100.0,200.0,300.0,,,
"""  # noqa: E501
    csv_file = tmp_path / "targets.csv"
    csv_file.write_text(csv_content)

    df = extract_point_target_data_from_source(csv_file)
    assert len(df) == 1


def test_convert_df_to_nominal_point_target():
    df = pd.DataFrame(
        {
            "target_name": ["T1"],
            "x_coord_m": [100.0],
            "y_coord_m": [200.0],
            "z_coord_m": [300.0],
            "delay_s": [0.0],
            "rcs_hh_dB": [0],
            "rcs_hv_dB": [0],
            "rcs_vh_dB": [0],
            "rcs_vv_dB": [0],
        }
    )
    pts = convert_df_to_nominal_point_target(df)
    assert len(pts) == 1
    assert pts[0].name == "T1"
    assert np.allclose(pts[0].xyz_coordinates, [100.0, 200.0, 300.0])
    assert pts[0].delay == 0.0


def test_convert_df_to_nominal_point_target_nan_delay():
    df = pd.DataFrame(
        {
            "target_name": ["T1"],
            "x_coord_m": [100.0],
            "y_coord_m": [200.0],
            "z_coord_m": [300.0],
            "delay_s": [np.nan],
            "rcs_hh_dB": [0],
            "rcs_hv_dB": [0],
            "rcs_vh_dB": [0],
            "rcs_vv_dB": [0],
        }
    )
    pts = convert_df_to_nominal_point_target(df)
    assert pts[0].delay is None


def test_convert_rosamond_file_to_compliant_csv_from_path(tmp_path):
    rosamond_csv = tmp_path / "rosamond.csv"
    rosamond_csv.write_text(
        '"Corner ID","Latitude (deg)","Longitude (deg)","Height Above Ellipsoid (m)",'
        '"Azimuth (deg)","Tilt / Elevation angle (deg)","Side Length (m)"\n'
        "00,34.79696931,-118.09653087,660.7853,170.50,12.10,2.4384\n"
        "01,34.79984857,-118.08698886,661.0342,170.50,8.72,2.4384\n"
    )

    measurement_date = PreciseDateTime.from_numeric_datetime(2024, 6, 1)
    result = convert_rosamond_file_to_compliant_csv(rosamond_csv, measurement_date)
    assert len(result) == 2
    assert "ROS00CR" in result["target_name"].values
    assert "ROS01CR" in result["target_name"].values
    assert result["target_type"].iloc[0] == "CR"
    assert result["target_shape"].iloc[0] == "trihedral"


def test_convert_rosamond_file_to_compliant_csv_from_dataframe():
    df = pd.DataFrame(
        {
            "Corner ID": [0, 1],
            "Latitude (deg)": [34.79696931, 34.79984857],
            "Longitude (deg)": [-118.09653087, -118.08698886],
            "Height Above Ellipsoid (m)": [660.7853, 661.0342],
            "Azimuth (deg)": [170.50, 170.50],
            "Tilt / Elevation angle (deg)": [12.10, 8.72],
            "Side Length (m)": [2.4384, 2.4384],
        }
    )

    measurement_date = PreciseDateTime.from_numeric_datetime(2024, 6, 1)
    result = convert_rosamond_file_to_compliant_csv(df, measurement_date)
    assert len(result) == 2
    assert "x_coord_m" in result.columns
    assert "y_coord_m" in result.columns
    assert "z_coord_m" in result.columns
