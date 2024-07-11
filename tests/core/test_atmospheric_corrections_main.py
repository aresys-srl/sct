# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing Atmospheric corrections computation"""

import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.configuration.sct_configuration import SCTPointTargetAnalysisConfig
from sct.core.atmospheric_corrections_main import (
    AtmosphericDelaysAcquisitionInfo,
    convert_atmospheric_delays_to_df,
    run_compute_atmospheric_delays,
)


class AtmCorrMainTestCase(unittest.TestCase):
    @mock.patch(
        "sct.core.atmospheric_corrections_core.inverse_geocoding_monostatic_core",
        mock.Mock(return_value=(PreciseDateTime.from_numeric_datetime(2000), None)),
    )
    @mock.patch("sct.core.atmospheric_corrections_core.ionosphere.compute_delay", mock.Mock(return_value=0.1))
    @mock.patch("sct.core.atmospheric_corrections_core.troposphere.compute_delay", mock.Mock(return_value=0.2))
    def test_run_compute_atmospheric_delays(self):
        nominal_target_coords = np.array([[-549463.4608500318, 132273.99706205435, 6331747.918866293]])

        class TestTrajectory:
            def evaluate(self, azimuth_times):
                return np.array([-609566.42264325, 146742.76442896, 7029012.78156523])

            def evaluate_first_derivatives(self, azimuth_times):
                return np.array([0, 0, 7000])

            def evaluate_second_derivatives(self, azimuth_times):
                return np.array([0, 0, 7000])

        acq_info = AtmosphericDelaysAcquisitionInfo(
            azimuth_time=PreciseDateTime.from_numeric_datetime(2000),
            carrier_frequency=1e9,
            trajectory=TestTrajectory(),
        )

        config = SCTPointTargetAnalysisConfig(
            enable_ionospheric_correction=True,
            enable_tropospheric_correction=True,
            ionospheric_maps_directory=Path("iono"),
            ionospheric_analysis_center="JPL",
            tropospheric_maps_directory=Path("tropo"),
        )

        iono_delay, tropo_delay = run_compute_atmospheric_delays(
            nominal_target_coords,
            acq_info,
            config,
        )
        self.assertAlmostEqual(iono_delay, 0.1)
        self.assertAlmostEqual(tropo_delay, 0.2)

    def test_convert_atmospheric_delays_to_df(self):
        targets = pd.DataFrame([["Name"]], columns=["target_name"])["target_name"]
        convert_atmospheric_delays_to_df(targets, delays=(np.array([0.1]), None))


if __name__ == "__main__":
    unittest.main()
