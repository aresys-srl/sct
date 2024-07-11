# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT automatic Unittest module
-----------------------------------------
"""
import unittest
from pathlib import Path

import shapely

from sct.analyses.automatic_analyses import CalibrationSite


class CalibrationSiteTestCase(unittest.TestCase):

    def test_calibration_site_init(self):

        site = CalibrationSite(
            name="NewSite",
            region=[],
            supported_analyses=["point_target_analysis"],
            reference_file=Path("pt.csv"),
            description="A site description",
        )

        self.assertEqual(site.name, "NewSite")
        self.assertEqual(site.region, [])
        self.assertEqual(site.supported_analyses, ["point_target_analysis"])
        self.assertEqual(site.reference_file, Path("pt.csv"))
        self.assertEqual(site.description, "A site description")

    def test_calibration_site_from_dict(self):
        input_dict = {
            "NewSite": {
                "latitude_boundaries_deg": [-5, 5],
                "longitude_boundaries_deg": [40, 45],
                "description": "A site description",
                "supported_analyses": ["point_target_analysis"],
                "reference_dataset": Path("pt.csv"),
            }
        }

        site = CalibrationSite.from_dict(input_dict)

        self.assertEqual(site.name, "NewSite")
        self.assertEqual(site.region, shapely.Polygon(((-5, 40), (-5, 45), (5, 40), (5, 45), (-5, 40))))
        self.assertEqual(site.supported_analyses, ["point_target_analysis"])
        self.assertEqual(site.reference_file, Path("pt.csv"))
        self.assertEqual(site.description, "A site description")


if __name__ == "__main__":
    unittest.main()
