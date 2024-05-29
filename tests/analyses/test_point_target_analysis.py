# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT point target analysis Unittest module
-----------------------------------------
"""
import unittest
from unittest import mock

import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime
from scipy.constants import speed_of_light

from sct.analyses.point_target_analysis import _compute_theoretical_rcs


class ComputeTheoreticalRCS(unittest.TestCase):
    """Test compute theoretical RCS"""

    @mock.patch("sct.analyses.point_target_analysis.compute_elevation_azimuth_wrt_enu", mock.Mock(return_value=(0, 0)))
    def test_compute_theoretical_rcs(self):
        """Test high level function"""
        carrier_frequency_hz = speed_of_light / 0.055

        class _TestTrajectory:
            def evaluate(self, _):
                return None

        columns_pt = [
            "target_name",
            "target_size_m",
            "corner_elevation_deg",
            "corner_azimuth_deg",
            "x_coord_m",
            "y_coord_m",
            "z_coord_m",
        ]
        data_pt = [
            [
                "ExampleName",
                0.7,
                -9.735599999999998,
                0,
                0,
                0,
                0,
            ]
        ]
        point_targets_df = pd.DataFrame(data_pt, columns=columns_pt)

        data = [
            ["ExampleName", PreciseDateTime.from_numeric_datetime(2000)],
        ]
        columns = ["target_name", "peak_azimuth_time_[UTC]"]
        data_df = pd.DataFrame(data, columns=columns)

        results = _compute_theoretical_rcs(data_df, point_targets_df, carrier_frequency_hz, _TestTrajectory())
        self.assertAlmostEqual(results[0], 24.56450589612527)


if __name__ == "__main__":
    unittest.main()
