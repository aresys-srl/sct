# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
CLI Radiometric Analysis commands.
----------------------------------
"""

import sys
from collections.abc import Callable
from pathlib import Path

import click
from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity

from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration
from sct.orchestration import (
    full_average_elevation_profiles_implementation,
    full_nesz_implementation,
    full_scalloping_implementation,
)


class RadiometricQuantity(click.ParamType):
    """Custom click type to manage radiometric quantities from string."""

    name = "radiometric_quantity"

    def convert(self, value, param, ctx) -> SARRadiometricQuantity:
        """Convert the input value to SARRadiometricQuantity."""
        try:
            return SARRadiometricQuantity[value.upper() + "_NOUGHT"]
        except ValueError:
            self.fail(f"{value!r} wrong input format", param, ctx)


def import_radiometric_2d_hist_plot() -> Callable:
    """Import the radiometric 2D histogram plotting function."""
    try:
        from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return radiometric_2D_hist_plot


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def radiometric_analysis(config) -> None:
    """Block-wise Radiometric Analysis."""


@radiometric_analysis.command("nesz")
@common.input_product_option
@common.output_directory_option
@common.generate_graph_option
@common.share_config
def radiometric_analysis_nesz(config: SCTConfiguration, product: Path, output_directory: Path, graphs: bool) -> None:
    """Noise Equivalent Sigma-Zero radiometric analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_ra_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Output folder is: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("NESZ   Analysis")

    radiometric_analysis_nesz_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@radiometric_analysis.command("elevation-profile")
@common.input_product_option
@common.output_directory_option
@click.option(
    "--output_radiometric_quantity",
    "-r",
    required=True,
    default=None,
    type=RadiometricQuantity(),
    help="Output radiometric quantity. It can be set to: beta, gamma, sigma",
)
@common.generate_graph_option
@common.share_config
def radiometric_analysis_average_profiles(
    config: SCTConfiguration,
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    graphs: bool,
) -> None:
    """Average Elevation Profiles radiometric analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_ra_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Output radiometric quantity is: {output_radiometric_quantity.name}")
    sct_logger.info(f"Output folder is: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Radiometric  Analysis")

    radiometric_analysis_average_profiles_implementation(
        product=product,
        output_radiometric_quantity=output_radiometric_quantity,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@radiometric_analysis.command("scalloping")
@common.input_product_option
@common.output_directory_option
@common.generate_graph_option
@common.share_config
def radiometric_analysis_scalloping(
    config: SCTConfiguration,
    product: Path,
    output_directory: Path,
    graphs: bool,
) -> None:
    """Scalloping Profiles radiometric analysis."""
    file_handler = (
        common.add_logging_file(output_directory.joinpath("sct_ra_analysis.log")) if config.general.save_log else None
    )
    enable_quality_logger(file_handler)

    sct_logger.info(f"Product: {product}")
    sct_logger.info(f"Output folder is: {output_directory}")
    sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

    common.display_title("Scalloping   Profiles")
    radiometric_analysis_scalloping_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("NESZ Analysis")
@common.graceful_exit("NESZ Analysis", "radiometric_analysis")
def radiometric_analysis_nesz_implementation(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the NESZ radiometric analysis command."""
    full_nesz_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs_func=import_radiometric_2d_hist_plot() if graphs else None,
    )


@common.log_elapsed_time("Average Elevation Profiles Analysis")
@common.graceful_exit("Average Elevation Profiles Analysis", "radiometric_analysis")
def radiometric_analysis_average_profiles_implementation(
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the average elevation profiles radiometric analysis command."""
    full_average_elevation_profiles_implementation(
        product=product,
        output_radiometric_quantity=output_radiometric_quantity,
        output_directory=output_directory,
        config=config,
        graphs_func=import_radiometric_2d_hist_plot() if graphs else None,
    )


@common.log_elapsed_time("Scalloping Profiles Analysis")
@common.graceful_exit("Scalloping Profiles Analysis", "radiometric_analysis")
def radiometric_analysis_scalloping_implementation(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the scalloping profiles radiometric analysis command."""
    full_scalloping_implementation(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs_func=import_radiometric_2d_hist_plot() if graphs else None,
    )
