# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing PTA Atmospheric corrections computation"""

from pathlib import Path

import numpy as np
import pandas as pd
from perseo_core.timing import PreciseDateTime

from sct.analyses.point_target.config import (
    IonosphericCorrectionsConf,
    SCTPointTargetAnalysisCorrectionsConf,
    TroposphericCorrectionsConf,
)
from sct.analyses.point_target.core.atmospheric_corrections_main import (
    AtmosphericDelaysAcquisitionInfo,
    convert_atmospheric_delays_to_df,
    run_compute_atmospheric_delays,
)


def test_run_compute_atmospheric_delays(mocker):
    mocker.patch(
        "sct.analyses.point_target.core.atmospheric_corrections_core.inverse_geocoding_monostatic",
        return_value=(PreciseDateTime.from_numeric_datetime(2000), None),
    )
    mocker.patch(
        "sct.analyses.point_target.core.atmospheric_corrections_core.ionosphere.compute_delay",
        return_value=0.1,
    )
    mocker.patch(
        "sct.analyses.point_target.core.atmospheric_corrections_core.troposphere.compute_delay",
        return_value=0.2,
    )

    nominal_target_coords = np.array([[-549463.4608500318, 132273.99706205435, 6331747.918866293]])

    class TestTrajectory:
        def position(self, azimuth_times):
            return np.array([-609566.42264325, 146742.76442896, 7029012.78156523])

        def velocity(self, azimuth_times):
            return np.array([0, 0, 7000])

        def acceleration(self, azimuth_times):
            return np.array([0, 0, 7000])

    acq_info = AtmosphericDelaysAcquisitionInfo(
        azimuth_time=PreciseDateTime.from_numeric_datetime(2000),
        carrier_frequency=1e9,
        trajectory=TestTrajectory(),
    )

    config = SCTPointTargetAnalysisCorrectionsConf(
        enable_ionospheric_correction=True,
        enable_tropospheric_correction=True,
        ionosphere=IonosphericCorrectionsConf(maps_directory=Path("iono"), analysis_center="JPL"),
        troposphere=TroposphericCorrectionsConf(maps_directory=Path("tropo")),
    )

    iono_delay, tropo_delay = run_compute_atmospheric_delays(
        nominal_target_coords,
        acq_info,
        config,
    )
    np.testing.assert_allclose(iono_delay, 0.1, atol=1e-3, rtol=0)
    np.testing.assert_allclose(tropo_delay, 0.2, atol=1e-3, rtol=0)


def test_convert_atmospheric_delays_to_df():
    targets = pd.DataFrame([["Name"]], columns=["target_name"])["target_name"]
    convert_atmospheric_delays_to_df(targets, delays=(np.array([0.1]), None))
