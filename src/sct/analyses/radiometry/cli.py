# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Command Line Interface for Radiometric Analysis."""

from __future__ import annotations

from pathlib import Path

import typer
from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.cli import common
from sct.configuration.config import GeneralConfiguration
from sct.configuration.logger import sct_logger

radiometric_app = typer.Typer(help="Block-wise Radiometric Analysis.")


@radiometric_app.command("nesz")
def radiometric_analysis_nesz(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
) -> None:
    """Noise Equivalent Sigma-Zero radiometric analysis."""

    config: GeneralConfiguration = ctx.obj

    log_path = output_directory / "sct_ra_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")
        sct_logger.info(f"Output folder is: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        common.display_title("NESZ   Analysis")

        analysis_config = (
            SCTRadiometricAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTRadiometricAnalysisConfig()
        )
        radiometric_analysis_nesz_implementation(
            product=product,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@radiometric_app.command("elevation-profiles")
def radiometric_analysis_average_profiles(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_radiometric_quantity: common.RadiometricQuantityOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
) -> None:
    """Average Elevation Profiles radiometric analysis."""

    output_radiometric_quantity = SARRadiometricQuantity[output_radiometric_quantity.upper() + "_NOUGHT"]

    config: GeneralConfiguration = ctx.obj

    log_path = output_directory / "sct_ra_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")
        sct_logger.info(f"Output radiometric quantity is: {output_radiometric_quantity.name}")
        sct_logger.info(f"Output folder is: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        common.display_title("Radiometric  Analysis")

        analysis_config = (
            SCTRadiometricAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTRadiometricAnalysisConfig()
        )
        radiometric_analysis_average_profiles_implementation(
            product=product,
            output_radiometric_quantity=output_radiometric_quantity,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@radiometric_app.command("rain-forest")
def radiometric_analysis_rain_forest(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
):
    """Rain Forest radiometric analysis (Gamma Profiles)."""
    return radiometric_analysis_average_profiles(
        ctx,
        product=product,
        output_radiometric_quantity="gamma",
        output_directory=output_directory,
        graphs=graphs,
    )


@radiometric_app.command("scalloping")
def radiometric_analysis_scalloping(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
) -> None:
    """Scalloping Profiles radiometric analysis."""

    config: GeneralConfiguration = ctx.obj

    log_path = output_directory / "sct_ra_analysis.log" if config.save_log else None

    with common.logging_to_file(log_path):
        sct_logger.info(f"Product: {product}")
        sct_logger.info(f"Output folder is: {output_directory}")
        sct_logger.info(f"Graphs generation {'enabled' if graphs else 'disabled'}")

        common.display_title("Scalloping   Profiles")

        analysis_config = (
            SCTRadiometricAnalysisConfig.from_toml(config.toml_path)
            if config.toml_path is not None
            else SCTRadiometricAnalysisConfig()
        )
        radiometric_analysis_scalloping_implementation(
            product=product,
            output_directory=output_directory,
            config=analysis_config,
            graphs=graphs,
            dump_config=config.save_config_copy,
        )


@common.log_elapsed_time("NESZ Analysis")
@common.graceful_exit("NESZ Analysis")
def radiometric_analysis_nesz_implementation(
    product: Path,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the NESZ radiometric analysis command."""
    from sct.analyses.radiometry.main import full_nesz_analysis

    full_nesz_analysis(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("Average Elevation Profiles Analysis")
@common.graceful_exit("Average Elevation Profiles Analysis")
def radiometric_analysis_average_profiles_implementation(
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the average elevation profiles radiometric analysis command."""
    from sct.analyses.radiometry.main import full_average_elevation_profiles_analysis

    full_average_elevation_profiles_analysis(
        product=product,
        output_radiometric_quantity=output_radiometric_quantity,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


@common.log_elapsed_time("Scalloping Profiles Analysis")
@common.graceful_exit("Scalloping Profiles Analysis")
def radiometric_analysis_scalloping_implementation(
    product: Path,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig,
    graphs: bool,
    dump_config: bool,
) -> None:
    """Implement the scalloping profiles radiometric analysis command."""
    from sct.analyses.radiometry.main import full_scalloping_analysis

    full_scalloping_analysis(
        product=product,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )
