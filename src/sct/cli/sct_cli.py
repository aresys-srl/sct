# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT CLI Tool.
-------------
"""

from pathlib import Path

import click

from sct.__init__ import __version__ as VERSION
from sct.cli.int_cli import interf_coherence_analysis
from sct.cli.notch_cli import pt_notch_analysis
from sct.cli.pta_cli import target_analysis
from sct.cli.ra_cli import radiometric_analysis
from sct.cli.sa_cli import spectral_analysis
from sct.cli.tar_cli import pt_ambiguity_ratio_analysis
from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTConfiguration

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
        ctx.ensure_object(SCTConfiguration)
        ctx.obj = SCTConfiguration()
    else:
        sct_logger.info(f"Using configuration file: {config}.")
        ctx.ensure_object(SCTConfiguration)
        ctx.obj = SCTConfiguration.from_toml(config)
    click.echo("\n")


sct_analysis.add_command(target_analysis)
sct_analysis.add_command(radiometric_analysis)
sct_analysis.add_command(interf_coherence_analysis)
sct_analysis.add_command(spectral_analysis)
sct_analysis.add_command(pt_ambiguity_ratio_analysis)
sct_analysis.add_command(pt_notch_analysis)
