# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing RCS computation"""

import unittest

import numpy as np

from sct.core.rcs_computation import compute_rcs_trihedral_corner_reflector


class RCSComputationTestCase(unittest.TestCase):
    """Testing rcs computation functionalities"""

    def setUp(self) -> None:
        self.cr_arm = 0.7
        self.wavelength = 0.055
        self.elevation_rad = np.array([0, np.pi / 4, np.pi / 3])
        self.azimuth_rad = np.array([0, np.pi / 4, np.pi / 3])

        # expected results
        self.rcs_expected_array = np.array([0.0, 286.0556891916635, 66.34793846512898])
        self.rcs_expected_invalid = np.array([0.0, np.nan, np.nan])

    def test_rcs_trihedral_scalar(self):
        rcs = compute_rcs_trihedral_corner_reflector(
            cr_arm_length_m=self.cr_arm,
            wavelength_m=self.wavelength,
            elevation_rad=self.elevation_rad[1],
            azimuth_rad=self.azimuth_rad[1],
        )
        self.assertIsInstance(rcs, float)
        np.testing.assert_allclose(rcs, self.rcs_expected_array[1], atol=1e-8, rtol=0)

    def test_rcs_trihedral_array(self):
        rcs = compute_rcs_trihedral_corner_reflector(
            cr_arm_length_m=self.cr_arm,
            wavelength_m=self.wavelength,
            elevation_rad=self.elevation_rad,
            azimuth_rad=self.azimuth_rad,
        )
        self.assertIsInstance(rcs, np.ndarray)
        self.assertEqual(rcs.size, self.elevation_rad.size)
        self.assertEqual(rcs.shape, self.elevation_rad.shape)
        np.testing.assert_allclose(rcs, self.rcs_expected_array, atol=1e-8, rtol=0)

    def test_rcs_trihedral_invalid(self):
        rcs = compute_rcs_trihedral_corner_reflector(
            cr_arm_length_m=self.cr_arm,
            wavelength_m=self.wavelength,
            elevation_rad=-self.elevation_rad,
            azimuth_rad=-self.azimuth_rad,
        )
        self.assertIsInstance(rcs, np.ndarray)
        self.assertEqual(rcs.size, self.elevation_rad.size)
        self.assertEqual(rcs.shape, self.elevation_rad.shape)
        np.testing.assert_allclose(rcs, self.rcs_expected_invalid, atol=1e-8, rtol=0)


if __name__ == "__main__":
    unittest.main()
