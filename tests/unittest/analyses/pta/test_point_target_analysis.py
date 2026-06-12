# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing SCT Point Target Analysis"""

import numpy as np
import pandas as pd
from perseo_core.timing import PreciseDateTime
from scipy.constants import speed_of_light

from sct.analyses.point_target.core.utilities import _compute_theoretical_rcs


def test_compute_theoretical_rcs(mocker):
    """Test high level function"""
    mocker.patch(
        "sct.analyses.point_target.core.utilities.compute_elevation_azimuth_wrt_enu",
        return_value=(0, 0),
    )
    carrier_frequency_hz = speed_of_light / 0.055

    class _TestTrajectory:
        def position(self, _):
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
    np.testing.assert_allclose(results[0], 24.56450589612527, atol=1e-9, rtol=0)
