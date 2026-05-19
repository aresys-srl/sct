# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing ETAD corrections computation"""

import unittest
from unittest import mock

import numpy as np
from shapely.geometry import Point

from sct.core.etad_corrections_main import _extract_etad_correction


class EtadCorrectionsTestCase(unittest.TestCase):
    """Unit tests for ETAD correction extraction using RegularGridInterpolator."""

    def test_extract_etad_correction_with_dummy_data(self):
        """Test _extract_etad_correction with dummy burst and location data.

        This test validates that the RegularGridInterpolator-based implementation
        correctly interpolates ETAD corrections at a given target location.
        """
        # Create dummy grid coordinates
        range_time = np.array([0.0, 0.5, 1.0, 1.5])  # 4 range time samples
        azimuth_time = np.array([0.0, 0.25, 0.5, 0.75, 1.0])  # 5 azimuth time samples

        # Create dummy correction grids: shape (len(azimuth_time), len(range_time))
        # Range corrections (X component)
        rng_corrections = np.array(
            [
                [1.0, 1.1, 1.2, 1.3],
                [1.05, 1.15, 1.25, 1.35],
                [1.1, 1.2, 1.3, 1.4],
                [1.15, 1.25, 1.35, 1.45],
                [1.2, 1.3, 1.4, 1.5],
            ]
        )
        # Azimuth corrections (Y component)
        az_corrections = np.array(
            [
                [2.0, 2.1, 2.2, 2.3],
                [2.05, 2.15, 2.25, 2.35],
                [2.1, 2.2, 2.3, 2.4],
                [2.15, 2.25, 2.35, 2.45],
                [2.2, 2.3, 2.4, 2.5],
            ]
        )

        # Create a mock burst object
        mock_burst = mock.Mock()

        # Query point coordinates (will be converted to SAR coordinates by mock)
        query_point = Point(0.0, 0.0, 0.0)

        # SAR time coordinates within the grid (should be interpolated)
        tau0 = 0.75  # range time coordinate (between 0.5 and 1.0)
        t0 = 0.4  # azimuth time coordinate (between 0.25 and 0.5)

        # Mock the geodetic_to_radar method
        mock_burst.geodetic_to_radar.return_value = (tau0, t0)

        # Mock get_burst_grid to return the dummy grids
        mock_burst.get_burst_grid.return_value = (azimuth_time, range_time)

        # Create a mock correction dictionary
        correction_dict = {"x": rng_corrections, "y": az_corrections}
        mock_burst.get_correction.return_value = correction_dict

        # Call the function under test
        rng_corr, az_corr = _extract_etad_correction(mock_burst, query_point)

        # Verify that the function was called and returns numeric values
        # RegularGridInterpolator returns 0-D numpy arrays for single-point queries
        self.assertTrue(isinstance(rng_corr, (float, np.ndarray, np.floating)))
        self.assertTrue(isinstance(az_corr, (float, np.ndarray, np.floating)))

        # Verify that interpolation produced reasonable values within expected ranges
        # For tau0=0.75 and t0=0.4, we expect interpolated values near the middle of the grid
        self.assertGreaterEqual(float(rng_corr), np.min(rng_corrections))
        self.assertLessEqual(float(rng_corr), np.max(rng_corrections))

        self.assertGreaterEqual(float(az_corr), np.min(az_corrections))
        self.assertLessEqual(float(az_corr), np.max(az_corrections))

        # Verify that mock methods were called with correct arguments
        mock_burst.geodetic_to_radar.assert_called_once()
        mock_burst.get_burst_grid.assert_called_once()
        mock_burst.get_correction.assert_called_once()

    def test_extract_etad_correction_corner_interpolation(self):
        """Test interpolation at grid corner points to ensure algorithm correctness.

        This validates that values at exact grid points are correctly reproduced.
        """
        # Create simple grid for exact validation
        range_time = np.array([0.0, 1.0])
        azimuth_time = np.array([0.0, 1.0])

        # Simple constant-gradient grid
        rng_corrections = np.array(
            [
                [10.0, 20.0],
                [30.0, 40.0],
            ]
        )
        az_corrections = np.array(
            [
                [100.0, 200.0],
                [300.0, 400.0],
            ]
        )

        mock_burst = mock.Mock()
        query_point = Point(0.0, 0.0, 0.0)

        # Test point at (0.0, 0.0) - should interpolate to [0,0] element
        tau0, t0 = 0.0, 0.0
        mock_burst.geodetic_to_radar.return_value = (tau0, t0)
        mock_burst.get_burst_grid.return_value = (azimuth_time, range_time)
        mock_burst.get_correction.return_value = {"x": rng_corrections, "y": az_corrections}

        rng_corr, az_corr = _extract_etad_correction(mock_burst, query_point)

        # At corner (0,0), should get the corner value
        np.testing.assert_allclose(float(rng_corr), 10.0, rtol=1e-6)
        np.testing.assert_allclose(float(az_corr), 100.0, rtol=1e-6)

        # Reset mock for next test
        mock_burst.reset_mock()
        mock_burst.geodetic_to_radar.return_value = (1.0, 1.0)
        mock_burst.get_burst_grid.return_value = (azimuth_time, range_time)
        mock_burst.get_correction.return_value = {"x": rng_corrections, "y": az_corrections}

        # Test point at (1.0, 1.0) - should interpolate to [1,1] element
        rng_corr, az_corr = _extract_etad_correction(mock_burst, query_point)

        # At corner (1,1), should get the opposite corner value
        np.testing.assert_allclose(float(rng_corr), 40.0, rtol=1e-6)
        np.testing.assert_allclose(float(az_corr), 400.0, rtol=1e-6)

    def test_extract_etad_correction_return_type(self):
        """Test that return values are numeric (not nested arrays).

        This validates that RegularGridInterpolator returns single values
        that can be easily converted to Python floats, unlike the old interp2d
        which returned 2-D arrays.
        """
        range_time = np.array([0.0, 1.0])
        azimuth_time = np.array([0.0, 1.0])
        rng_corrections = np.ones((2, 2)) * 5.0
        az_corrections = np.ones((2, 2)) * 10.0

        mock_burst = mock.Mock()
        query_point = Point(0.0, 0.0, 0.0)

        mock_burst.geodetic_to_radar.return_value = (0.5, 0.5)
        mock_burst.get_burst_grid.return_value = (azimuth_time, range_time)
        mock_burst.get_correction.return_value = {"x": rng_corrections, "y": az_corrections}

        rng_corr, az_corr = _extract_etad_correction(mock_burst, query_point)

        # Verify both can be converted to Python floats (0-D arrays or native floats)
        rng_val = float(rng_corr)
        az_val = float(az_corr)

        # Verify values are as expected
        np.testing.assert_allclose(rng_val, 5.0, rtol=1e-6)
        np.testing.assert_allclose(az_val, 10.0, rtol=1e-6)


if __name__ == "__main__":
    unittest.main()
