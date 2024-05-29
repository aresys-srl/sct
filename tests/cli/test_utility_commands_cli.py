# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Auxiliary CLI tools unittest
--------------------------------
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from sct.cli.utility_commands_cli import (
    sct_ionex_map_downloader,
    sct_rosamond_dataset_converter,
    sct_tropospheric_map_downloader,
)


class AuxiliaryCLITestCase(unittest.TestCase):
    """Test command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()

    def test_download_vmf3(self):
        """Download vmf3 files"""
        command = ["-d", "2024-04-20 10:00:00"]
        with TemporaryDirectory() as out_dir:
            command.extend(f"-r COARSE -out {out_dir}".split())
            result = self.cli_runner.invoke(sct_tropospheric_map_downloader, command)
            self.assertEqual(result.exit_code, 0)

            files = [Path(line) for line in result.stdout.splitlines() if "VMF3_" in line]
            self.assertEqual(len(files), 4)
            self.assertTrue(files[0].exists())
            self.assertTrue(files[1].exists())
            self.assertTrue(files[2].exists())
            self.assertTrue(files[3].exists())

    def test_download_ionex_error_non_existing_email(self):
        """Error on server side on non existing email"""
        command = ["-d", "2024-04-20 10:00:00"]
        with TemporaryDirectory() as out_dir:
            command.extend(f"-c JPL -e name@domain.it -out {out_dir}".split())
            result = self.cli_runner.invoke(sct_ionex_map_downloader, command)
            self.assertEqual(result.exit_code, -1)

    def test_rosamond_converter(self):
        rosamond_out = """ "Corner ID","Latitude (deg)","Longitude (deg)","Height Above Ellipsoid (m)","Azimuth (deg)","Tilt / Elevation angle (deg)","Side Length (m)", "Epoch: 2024-05-24 00:00"
        00,34.79696931,-118.09653087,660.7853,170.50,12.10,2.4384
        01,34.79984857,-118.08698886,661.0342,170.50,8.72,2.4384
        02,34.80523758,-118.08738926,660.7955,170.00,9.30,2.4384"""
        with TemporaryDirectory() as tmp_dir:
            input_csv = Path(tmp_dir).joinpath("rosamond.csv")
            input_csv.write_text(rosamond_out)
            command = f"-s {input_csv} -d".split() + ["2024-05-24 00:00:00"]
            result = self.cli_runner.invoke(sct_rosamond_dataset_converter, command)
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path(tmp_dir).joinpath("rosamond_point_target.csv"))


if __name__ == "__main__":
    unittest.main()
