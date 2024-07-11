# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT S1 custom corrections
-------------------------
"""

import sys
import unittest
from enum import Enum
from pathlib import Path

import pandas as pd
from arepytools.timing.precisedatetime import PreciseDateTime

from sct.core.custom_corrections.sentinel_1_ipf import (
    _detect_mid_swath_channel,
    _get_rid_of_pol_dependency,
    compute_azimuth_corrections,
    compute_range_corrections,
)


class S1IPFTestCase(unittest.TestCase):
    """Test command line interface"""

    def setUp(self) -> None:
        class TestProduct:
            channels_list = [1]

            def get_channel_data(self, channel_id):
                class TestChannelData:
                    class TestChannel:
                        class TestBurstInfo:
                            num = 1
                            range_start_times = [0.2]

                        burst_info = TestBurstInfo()

                    class TestEnums(Enum):
                        HH = "H/H"

                    swath_name = "SwathName"
                    polarization = TestEnums.HH
                    swst_changes = ()
                    pulse_latch_time = 0.1
                    pulse_rate = 3e10
                    _channel = TestChannel()

                    def get_mid_burst_times(self):
                        return PreciseDateTime.from_numeric_datetime(2000), 0.5

                return TestChannelData

            swst_changes = [PreciseDateTime.from_numeric_datetime(2000), 0.5]
            pulse_latch_time = 0.1

        self.product = TestProduct()

        columns = [
            "id",
            "ground_velocity_[ms]",
            "total_doppler_frequency_[Hz]",
            "doppler_rate_real_[Hzs]",
            "doppler_rate_theoretical_[Hzs]",
            "peak_azimuth_time_[UTC]",
            "peak_range_time_[s]",
            "channel",
            "burst",
        ]
        values = [[0, 7000, 10000, -5000, -4999, str(PreciseDateTime.from_numeric_datetime(2000)), 0.51, 1, 0]]
        self.data = pd.DataFrame(values, columns=columns)

    def test_detect_mid_swath_channel(self):
        """Test mid swath channel detection"""
        self.assertEqual(_detect_mid_swath_channel(["IW2", "IW1", "IW3"]), "IW2")
        self.assertEqual(_detect_mid_swath_channel(["EW5", "EW3", "EW1", "EW4", "EW2"]), "EW3")
        self.assertEqual(_detect_mid_swath_channel(["EW5"]), "EW5")

    def test_get_rid_of_pol_dependency(self):
        """Test get rid of pol dependency"""
        arg = {"key0": {"inner_key": (PreciseDateTime.from_numeric_datetime(2000), 0.5)}}
        self.assertEqual(_get_rid_of_pol_dependency(arg), {"key0": (PreciseDateTime.from_numeric_datetime(2000), 0.5)})

    def test_compute_range_corrections(self):
        output = compute_range_corrections(self.product, self.data)
        self.assertAlmostEqual(output["doppler_shift_range_correction_[m]"][0], -49.96540966666667)

    def test_compute_azimuth_corrections(self):
        output = compute_azimuth_corrections(self.product, self.data)
        self.assertAlmostEqual(output["fm_rate_shift_azimuth_correction_[m]"][0], -2.800560112021773)


if __name__ == "__main__":
    unittest.main()
