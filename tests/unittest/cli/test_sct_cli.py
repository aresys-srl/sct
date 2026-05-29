# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT Command Line Interface unit tests"""

from typer.testing import CliRunner

from sct import __version__ as VERSION
from sct.cli.cli import app

cli_runner = CliRunner()


def test_error_no_args():
    """Display help when no arguments are provided"""
    result = cli_runner.invoke(app)
    assert result.exit_code == 2


def test_display_help():
    """Display help"""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_display_version():
    """Display version"""
    result = cli_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert VERSION in result.output
