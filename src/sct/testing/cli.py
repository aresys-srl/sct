# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Testing CLI Utility
-------------------
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from sct import __version__
from sct.cli import common
from sct.plugins import available_plugins
from sct.testing.run import run_tests, summary_results

testing_app = typer.Typer(
    help="SCT Testing Interface.",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)

RegistryOption = Annotated[
    Path,
    typer.Option(
        ...,
        "--registry",
        "-r",
        exists=True,
        dir_okay=False,
        file_okay=True,
        resolve_path=True,
        help="Path to the testing registry containing the tests to be run",
    ),
]

CLIOption = Annotated[
    bool,
    typer.Option(
        "--cli",
        "-c",
        help="Flag to perform analysis using the SCT CLI tool instead of the API",
    ),
]

OutputDirectoryOption1 = Annotated[
    Path | None,
    typer.Option(
        "--output-directory",
        "-out",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Path to the folder where to save output data",
    ),
]


@testing_app.command("test")
def integration_testing(
    registry: RegistryOption,
    output_directory: OutputDirectoryOption1,
    cli: CLIOption = False,
    graphs: common.GraphsOption = False,
) -> None:
    """Run SCT integration tests procedure from registry."""
    common.display_title("SCT Integration Tests")

    typer.echo(f"SCT Version: {__version__}\n")

    typer.echo("Installed plugins detected:\n")

    for name in available_plugins:
        typer.echo(name)
        typer.echo()

    if not output_directory.exists():
        typer.echo("Output directory not found: creating the output folder.")
        output_directory.mkdir(parents=True)

    results = run_tests(registry_path=registry, output_dir=output_directory, cli=cli, graphs=graphs)

    common.display_title("Summary")

    outcome = summary_results(results=results)

    if outcome:
        typer.Exit(0)
    else:
        typer.Exit(1)
