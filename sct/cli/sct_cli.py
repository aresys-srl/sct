# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT CLI Tool
------------
"""

import logging
from pathlib import Path
from typing import Optional

import click

from sct.__init__ import __version__ as VERSION
from sct.cli.nesz_cli import nesz_analysis
from sct.cli.pta_cli import target_analysis
from sct.configuration.sct_default_configuration import SCTConfiguration

version_option = click.version_option(VERSION, help="Show CLI version and exit")

# creating a decorator to pass a SCTConfiguration dataclass object between commands
share_config = click.make_pass_decorator(SCTConfiguration)

# syncing with logger
log = logging.getLogger("quality_analysis")


@click.group(
    context_settings=dict(
        help_option_names=["-h", "--help"],
    )
)
@version_option
@click.pass_context
@click.option(
    "-cfg",
    "--config",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Path to the configuration file with settings.",
)
def sct_analysis(ctx: click.Context, config: Optional[Path]):
    """SCT tool for SAR products quality analysis"""
    click.echo("Starting application...\n")
    if config is None:
        log.info("Configuration not provided. Using default one.")
        ctx.ensure_object(SCTConfiguration)
        ctx.obj = SCTConfiguration()
    else:
        log.info("Using the custom configuration file provided.")
        ctx.ensure_object(SCTConfiguration)
        ctx.obj = SCTConfiguration.from_toml(config)


sct_analysis.add_command(target_analysis)
sct_analysis.add_command(nesz_analysis)
