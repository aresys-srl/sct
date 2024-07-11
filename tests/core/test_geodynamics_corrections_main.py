# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing Geodynamics corrections computation"""

import unittest
from unittest import mock

import numpy as np
import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core.geodynamics_corrections_main import run_compute_geodynamics_corrections


class GeoCorrMainTestCase(unittest.TestCase):
    @mock.patch(
        "arepyextras.perturbations.geodynamics.solid_tides.compute_displacement",
        mock.Mock(return_value=np.array([[0.02881661, -0.00969161, -0.12631474]])),
    )
    def test_run_compute_geodynamics_corrections(self):
        nominal_target_coords = np.array([[-549463.4608500318, 132273.99706205435, 6331747.918866293]])
        acquisition_time = PreciseDateTime.from_numeric_datetime(2000)
        columns = ["validity_start_date", "validity_stop_date", "measurement_date", "plate"]
        values = [
            [
                PreciseDateTime.from_numeric_datetime(1999),
                PreciseDateTime.from_numeric_datetime(2001),
                PreciseDateTime.from_numeric_datetime(2000, hours=1),
                "EURA",
            ]
        ]
        pt_df = pd.DataFrame(values, columns=columns)
        run_compute_geodynamics_corrections(
            nominal_target_coords, acquisition_time, pt_df, SCTPointTargetAnalysisConfig()
        )


if __name__ == "__main__":
    unittest.main()
