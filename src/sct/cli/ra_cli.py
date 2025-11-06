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
from perseo_quality.radiometric_analysis.block_wise.support import (
    radiometric_profiles_to_netcdf,
    radiometric_statistical_analysis_to_df,
)
from perseo_quality.radiometric_analysis.custom_dataclasses import RadiometricProfilesOutput

import sct.analyses.radiometric_analysis as ra
from sct.cli import common
from sct.configuration.logger import enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


class RadiometricQuantity(click.ParamType):
    """Custom click type to manage radiometric quantities from string."""

    name = "radiometric_quantity"

    def convert(self, value, param, ctx) -> SARRadiometricQuantity:
        """Convert the input value to SARRadiometricQuantity."""
        try:
            return SARRadiometricQuantity[value.upper() + "_NOUGHT"]
        except ValueError:
            self.fail(f"{value!r} wrong input format", param, ctx)


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
def radiometric_analysis_nesz_implementation(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the NESZ radiometric analysis command."""
    if graphs:
        radiometric_2d_hist_plot = import_radiometric_2d_hist_plot()

    output = ra.nesz_analysis(product_path=product, config=config.radiometric_analysis)

    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="radiometric_analysis")

    save_and_plot_results(
        output=output,
        output_directory=output_directory,
        graphs=graphs,
        radiometric_2d_hist_plot=radiometric_2d_hist_plot,
        tag="NESZ",
    )


@common.log_elapsed_time("Average Elevation Profiles Analysis")
def radiometric_analysis_average_profiles_implementation(
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the average elevation profiles radiometric analysis command."""
    if graphs:
        radiometric_2d_hist_plot = import_radiometric_2d_hist_plot()

    output = ra.average_elevation_profile_analysis(
        product_path=product,
        output_quantity=output_radiometric_quantity,
        config=config.radiometric_analysis,
    )

    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="radiometric_analysis")

    save_and_plot_results(
        output=output,
        output_directory=output_directory,
        graphs=graphs,
        radiometric_2d_hist_plot=radiometric_2d_hist_plot,
        tag=f"AVERAGE_{output_radiometric_quantity.name}",
    )


@common.log_elapsed_time("Scalloping Profiles Analysis")
def radiometric_analysis_scalloping_implementation(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs: bool,
) -> None:
    """Implement the scalloping profiles radiometric analysis command."""
    if graphs:
        radiometric_2d_hist_plot = import_radiometric_2d_hist_plot()

    output = ra.scalloping_analysis(product_path=product, config=config.radiometric_analysis)

    if config.general.save_config_copy:
        config.dump_to_toml(out_file=output_directory.joinpath("analysis_config.toml"), selected="radiometric_analysis")

    save_and_plot_results(
        output=output,
        output_directory=output_directory,
        graphs=graphs,
        radiometric_2d_hist_plot=radiometric_2d_hist_plot,
        tag="SCALLOPING",
    )


def save_and_plot_results(
    output: list[RadiometricProfilesOutput],
    output_directory: Path,
    graphs: bool,
    radiometric_2d_hist_plot: Callable,
    tag: str,
) -> None:
    """Save results to netCDF and plot graphs if required."""
    if graphs:
        sct_logger.info("Saving results to netCDF and plotting graphs...")
    else:
        sct_logger.info("Saving results to netCDF format...")

    stats_df = radiometric_statistical_analysis_to_df(data=output)
    stats_df.to_csv(output_directory.joinpath("radiometry_statistics.csv"), index=False)

    for item in output:
        radiometric_profiles_to_netcdf(data=item, out_path=output_directory, tag=tag)

        if graphs:
            assert item.polarization is not None
            radiometric_2d_hist_plot(
                data=item,
                out_dir=output_directory,
                title=f"{tag.upper()} Profiles {item.general_info.channel}",
            )


def import_radiometric_2d_hist_plot() -> Callable:
    """Import the radiometric 2D histogram plotting function."""
    try:
        from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
    except ImportError:
        sct_logger.critical('Install graphs requirements "pip install sct[graphs]"')
        sys.exit(1)

    return radiometric_2D_hist_plot
