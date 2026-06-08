"""Testing point target analysis utility functions"""

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.analyses.point_target.core.utilities import (
    update_df_with_llh,
    update_results_with_derived_quantities,
    update_results_with_theoretical_rcs,
    update_targets_with_geodynamics_corrections,
)


def test_update_df_with_llh():
    results = pd.DataFrame(
        {
            "target_name": ["T1", "T2"],
            "acquisition_mode": ["SM", "IW"],
            "some_result": [1.0, 2.0],
        }
    )
    point_targets_df = pd.DataFrame(
        {
            "target_name": ["T1", "T2"],
            "latitude_deg": [45.0, 46.0],
            "longitude_deg": [9.0, 10.0],
            "altitude_m": [100.0, 200.0],
        }
    )

    updated = update_df_with_llh(results, point_targets_df)
    assert "latitude_deg" in updated.columns
    assert "longitude_deg" in updated.columns
    assert "altitude_m" in updated.columns
    assert updated.loc[0, "latitude_deg"] == 45.0


def test_update_results_with_derived_quantities():
    results = pd.DataFrame(
        {
            "some_range_correction_[m]": [0.1, 0.2],
            "other_range_correction_[m]": [0.3, 0.4],
            "some_azimuth_correction_[m]": [0.5, 0.6],
            "slant_range_localization_error_[m]": [1.0, 2.0],
            "azimuth_localization_error_[m]": [3.0, 4.0],
        }
    )

    updated = update_results_with_derived_quantities(results)
    assert "total_ale_range_correction_[m]" in updated.columns
    assert "total_ale_azimuth_correction_[m]" in updated.columns
    assert "revised_ale_range_[m]" in updated.columns
    assert "revised_ale_azimuth_[m]" in updated.columns
    assert updated.loc[0, "total_ale_range_correction_[m]"] == pytest.approx(0.4)
    assert updated.loc[0, "total_ale_azimuth_correction_[m]"] == pytest.approx(0.5)
    assert updated.loc[0, "revised_ale_range_[m]"] == pytest.approx(1.4)
    assert updated.loc[0, "revised_ale_azimuth_[m]"] == pytest.approx(3.5)


def test_update_results_with_theoretical_rcs(monkeypatch):
    results = pd.DataFrame(
        {
            "target_name": ["T1"],
            "rcs_[dB]": [20.0],
        }
    )
    point_targets_df = pd.DataFrame(
        {
            "target_name": ["T1"],
            "target_size_m": [0.7],
            "corner_elevation_deg": [35.0],
            "corner_azimuth_deg": [0.0],
        }
    )

    class MockTrajectory:
        def evaluate(self, _):
            return np.array([0, 0, 0])

    class MockChannelData:
        carrier_frequency = 5.4e9
        trajectory = MockTrajectory()

    monkeypatch.setattr(
        "sct.analyses.point_target.core.utilities._compute_theoretical_rcs",
        mock.Mock(return_value=[24.5]),
    )

    update_results_with_theoretical_rcs(results, point_targets_df, MockChannelData())
    assert "rcs_error_[dB]" in results.columns
    assert "rcs_theoretical_[dB]" in results.columns
    assert results.loc[0, "rcs_theoretical_[dB]"] == 24.5


def test_update_results_with_theoretical_rcs_no_info():
    results = pd.DataFrame(
        {
            "target_name": ["T1"],
            "rcs_[dB]": [20.0],
        }
    )
    point_targets_df = pd.DataFrame(
        {
            "target_name": ["T1"],
        }
    )

    class MockChannelData:
        carrier_frequency = 5.4e9

    update_results_with_theoretical_rcs(results, point_targets_df, MockChannelData())
    assert "rcs_theoretical_[dB]" in results.columns
    assert results.loc[0, "rcs_theoretical_[dB]"] is None


def test_update_targets_with_geodynamics_corrections(monkeypatch):
    class MockAzimuthAxis:
        @property
        def size(self):
            return 1

        def __getitem__(self, _):
            return 0.0

    class MockFirstChannel:
        azimuth_axis = MockAzimuthAxis()

    point_targets_df = pd.DataFrame(
        {
            "x_coord_m": [100.0],
            "y_coord_m": [200.0],
            "z_coord_m": [300.0],
        }
    )
    nominal_target_coords = np.array([[100.0, 200.0, 300.0]])
    config = SCTPointTargetAnalysisConfig()

    monkeypatch.setattr(
        "sct.analyses.point_target.core.utilities.run_compute_geodynamics_corrections",
        mock.Mock(return_value=np.array([[1.0, 2.0, 3.0]])),
    )

    update_targets_with_geodynamics_corrections(
        MockFirstChannel(),
        point_targets_df,
        nominal_target_coords,
        config,
    )
    assert point_targets_df.loc[0, "x_coord_m"] == 101.0
    assert point_targets_df.loc[0, "y_coord_m"] == 202.0
    assert point_targets_df.loc[0, "z_coord_m"] == 303.0
