# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT S1 custom corrections
-------------------------
"""

import unittest

from arepytools.timing.precisedatetime import PreciseDateTime

from sct.core.custom_corrections.sentinel_1_ipf import _detect_mid_swath_channel, _get_rid_of_pol_dependency


class S1IPFTestCase(unittest.TestCase):
    """Test command line interface"""

    def test_detect_mid_swath_channel(self):
        """Test mid swath channel detection"""
        self.assertEqual(_detect_mid_swath_channel(["IW2", "IW1", "IW3"]), "IW2")
        self.assertEqual(_detect_mid_swath_channel(["EW5", "EW3", "EW1", "EW4", "EW2"]), "EW3")
        self.assertEqual(_detect_mid_swath_channel(["EW5"]), "EW5")

    def test_get_rid_of_pol_dependency(self):
        """Test get rid of pol dependency"""
        arg = {"key0": {"inner_key": (PreciseDateTime.from_numeric_datetime(2000), 0.5)}}
        self.assertEqual(_get_rid_of_pol_dependency(arg), {"key0": (PreciseDateTime.from_numeric_datetime(2000), 0.5)})


if __name__ == "__main__":
    unittest.main()
