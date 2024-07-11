# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT SCT CLI unittest
--------------------
"""

import unittest

from click.testing import CliRunner

from sct import __version__ as VERSION
from sct.cli.sct_cli import sct_analysis


class SCTCLITestCase(unittest.TestCase):
    """Test command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()

    def test_error_no_args(self):
        """Display help when no arguments are provided"""
        result = self.cli_runner.invoke(sct_analysis)
        self.assertEqual(result.exit_code, 0)

    def test_display_help(self):
        """Display help"""
        result = self.cli_runner.invoke(sct_analysis, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_version(self):
        """Display version"""
        result = self.cli_runner.invoke(sct_analysis, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(VERSION in result.output)


if __name__ == "__main__":
    unittest.main()
