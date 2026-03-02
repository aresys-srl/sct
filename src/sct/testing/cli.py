# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Testing CLI Utility
-------------------
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from sct import __version__
from sct.cli import common
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.io.input_product_plugins import import_input_product_plugins
from sct.testing.run import run_tests, summary_results

enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")


def integration_testing() -> None:
    """Entry point for sct integration testing module using test registry."""
    sct_integration_testing_run()


# INTEGRATIONS TESTING
@click.command(
    name="sct-testing",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.option(
    "--registry",
    "-r",
    required=True,
    type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=False),
    help="Path to the testing registry containing the tests to be run",
)
@click.option(
    "--output_directory",
    "-out",
    required=False,
    default=None,
    type=click.Path(path_type=Path, dir_okay=True),
    help="Path to the folder where to save output data",
)
@click.option(
    "--cli",
    "-c",
    default=False,
    is_flag=True,
    type=bool,
    help="Flag to perform analysis using the SCT CLI tool instead of the API",
)
@common.generate_graph_option
def sct_integration_testing_run(registry: Path, output_directory: Path, cli: bool, graphs: bool) -> None:
    """Run SCT integration tests procedure from registry."""
    common.display_title("SCT Integration Tests")

    click.echo(f"SCT Version: {__version__}\n")

    click.echo("Installed plugins detected:\n")

    for name in import_input_product_plugins(additional_plugins=[]):
        click.echo(name)
        click.echo()

    if not output_directory.exists():
        click.echo("Output directory not found: creating the output folder.")
        output_directory.mkdir(parents=True)

    results = run_tests(registry_path=registry, output_dir=output_directory, cli=cli, graphs=graphs)

    common.display_title("Summary")

    outcome = summary_results(results=results)

    if outcome:
        sys.exit(0)
    else:
        sys.exit(-1)
