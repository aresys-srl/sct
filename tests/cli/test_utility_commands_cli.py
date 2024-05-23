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

from sct.cli.utility_commands_cli import sct_ionex_map_downloader, sct_tropospheric_map_downloader


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


if __name__ == "__main__":
    unittest.main()
