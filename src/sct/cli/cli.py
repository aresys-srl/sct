# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT CLI Tool
------------
"""

from __future__ import annotations

from pathlib import Path

import typer

from sct.__init__ import __version__ as VERSION
from sct.cli.utilities import utilities_app
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger
from sct.core.registry import ANALYSIS_REGISTRY
from sct.testing.cli import testing_app

app = typer.Typer(
    help="SCT tool for SAR products quality analysis.",
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120},
)


@app.callback()
def main(
    ctx: typer.Context,
    config: Path | None = typer.Option(
        None,
        "--config",
        "-cfg",
        exists=True,
        dir_okay=False,
        help="Path to the configuration file with settings.",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        callback=lambda v: typer.echo(VERSION) or raise_exit() if v else None,
        is_eager=True,
        help="Show CLI version and exit",
    ),
):
    typer.echo("Starting application...\n")

    if config is None:
        sct_logger.info("Configuration not provided. Using default configuration.")
        ctx.obj = GeneralConfiguration()
    else:
        sct_logger.info(f"Using configuration file: {config}.")
        ctx.obj = GeneralConfiguration.from_toml(config)

    typer.echo("\n")


def raise_exit():
    raise typer.Exit()


registered_typer_apps = set()
app.add_typer(utilities_app, name="auxiliary")
app.add_typer(testing_app, name="testing")
for name, item in ANALYSIS_REGISTRY.items():
    if item.cli is not None:
        if isinstance(item.cli, typer.Typer):
            # Only add if we haven't already
            if id(item.cli) not in registered_typer_apps:
                app.add_typer(item.cli, name=item.cli_group_name)
                registered_typer_apps.add(id(item.cli))
        else:
            # fallback for function-based commands
            app.command(name=name)(item.cli)
