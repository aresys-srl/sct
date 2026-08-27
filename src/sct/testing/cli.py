# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Command Line Interface for SCT Testing feature."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from sct import __version__
from sct.cli import common
from sct.plugins import get_available_analyses_plugins, get_available_product_format_plugins
from sct.testing.run import run_tests
from sct.testing.utils import safe_rule_printing, summary_results

console = Console()

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

    safe_rule_printing("[bold blue]⚙️ Environment Details[/bold blue]", "[bold blue]Environment Details[/bold blue]")

    console.print(f"[bold]SCT Version:[/bold] [bold green]{__version__}[/bold green]\n")

    console.print("[bold]Installed plugins detected:\n[/bold]")

    for plugin in get_available_product_format_plugins():
        console.print(f"[italic]{plugin.__name__}[/italic] - [bold]v{plugin.version}[/bold]")

    typer.echo()
    console.print("[bold]Installed analysis plugins detected:\n[/bold]")

    for plugin in get_available_analyses_plugins():
        console.print(f"[italic]{plugin.__name__}[/italic] - [bold]v{plugin.version}[/bold]")
        typer.echo()
    typer.echo()

    if not output_directory.exists():
        typer.echo("Output directory not found: creating the output folder.")
        output_directory.mkdir(parents=True)

    safe_rule_printing("[bold cyan]🧪 Running Tests[/bold cyan]", "[bold cyan]Running Tests[/bold cyan]")

    results = run_tests(registry_path=registry, output_dir=output_directory, cli=cli, graphs=graphs)

    outcome = summary_results(results=results)

    if outcome:
        sys.exit(0)
    else:
        sys.exit(1)
