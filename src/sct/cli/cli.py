# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT CLI Tool
------------
"""

from __future__ import annotations

from pathlib import Path

import click

from sct.__init__ import __version__ as VERSION
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger
from sct.core.registry import ANALYSIS_REGISTRY

version_option = click.version_option(VERSION, help="Show CLI version and exit")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@version_option
@click.pass_context
@click.option(
    "-cfg",
    "--config",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Path to the configuration file with settings.",
)
def sct_analysis(ctx: click.Context, config: Path | None) -> None:
    """SCT tool for SAR products quality analysis."""
    click.echo("Starting application...\n")
    if config is None:
        sct_logger.info("Configuration not provided. Using default configuration.")
        ctx.ensure_object(GeneralConfiguration)
        ctx.obj = GeneralConfiguration()
    else:
        sct_logger.info(f"Using configuration file: {config}.")
        ctx.ensure_object(GeneralConfiguration)
        ctx.obj = GeneralConfiguration.from_toml(config)
    click.echo("\n")


for item in ANALYSIS_REGISTRY.values():
    if item.cli_command is not None:
        if item.cli_command.name not in sct_analysis.commands:
            sct_analysis.add_command(item.cli_command)
