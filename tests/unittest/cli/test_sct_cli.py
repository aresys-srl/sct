# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT SCT CLI unittest
--------------------
"""

import unittest

from typer.testing import CliRunner

from sct import __version__ as VERSION
from sct.cli.cli import app


class SCTCLITestCase(unittest.TestCase):
    """Test command line interface"""

    def setUp(self) -> None:
        self.cli_runner = CliRunner()

    def test_error_no_args(self):
        """Display help when no arguments are provided"""
        result = self.cli_runner.invoke(app)
        self.assertEqual(result.exit_code, 2)

    def test_display_help(self):
        """Display help"""
        result = self.cli_runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)

    def test_display_version(self):
        """Display version"""
        result = self.cli_runner.invoke(app, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(VERSION in result.output)


if __name__ == "__main__":
    unittest.main()
