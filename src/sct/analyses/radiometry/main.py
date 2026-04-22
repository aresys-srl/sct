# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis implementation
-----------------------
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
from perseo_quality.radiometric_analysis.block_wise.support import (
    radiometric_profiles_to_netcdf,
    radiometric_statistical_analysis_to_df,
)
from perseo_quality.radiometric_analysis.custom_dataclasses import RadiometricProfilesOutput

from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig
from sct.analyses.radiometry.core import (
    sct_average_elevation_profile_analysis,
    sct_nesz_analysis,
    sct_scalloping_analysis,
)
from sct.configuration.logger import sct_logger


def full_nesz_analysis(
    product: Path,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig | None,
    graphs: bool,
) -> tuple[Path, Path]:
    """Full implementation of Noise Equivalent Sigma-Zero (NESZ) Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_directory : Path
        Path to the output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    graphs_func = _import_ra_graphs_func(graphs)
    output = sct_nesz_analysis(
        product_path=product,
        config=config,
    )
    return _ra_save_and_plot_results(
        output=output, output_directory=output_directory, graphs_func=graphs_func, tag="NESZ", plot_mode="min"
    )


def full_average_elevation_profiles_analysis(
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig | None,
    graphs: bool,
) -> tuple[Path, Path]:
    """Full implementation of Average Radiometric Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_radiometric_quantity : SARRadiometricQuantity
        output radiometric quantity selected
    output_directory : Path
        Path to the output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    graphs_func = _import_ra_graphs_func(graphs)
    output = sct_average_elevation_profile_analysis(
        product_path=product,
        output_quantity=output_radiometric_quantity,
        config=config,
    )
    return _ra_save_and_plot_results(
        output=output,
        output_directory=output_directory,
        graphs_func=graphs_func,
        tag=f"AVERAGE_{output_radiometric_quantity.name}",
        plot_mode="mean",
    )


def full_rain_forest_analysis(
    product: Path,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig | None,
    graphs: bool,
) -> tuple[Path, Path]:
    """Full implementation of Rain Forest Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_directory : Path
        Path to the output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    return full_average_elevation_profiles_analysis(
        product=product,
        output_radiometric_quantity=SARRadiometricQuantity.GAMMA_NOUGHT,
        output_directory=output_directory,
        config=config,
        graphs=graphs,
    )


def full_scalloping_analysis(
    product: Path,
    output_directory: Path,
    config: SCTRadiometricAnalysisConfig | None,
    graphs: bool,
) -> tuple[Path, Path]:
    """Full implementation of Scalloping Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_directory : Path
        Path to the output directory
    config : SCTRadiometricAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    graphs_func = _import_ra_graphs_func(graphs)
    output = sct_scalloping_analysis(product_path=product, config=config)
    return _ra_save_and_plot_results(
        output=output, output_directory=output_directory, graphs_func=graphs_func, tag="SCALLOPING", plot_mode="mean"
    )


def _import_ra_graphs_func(graphs: bool) -> Callable | None:
    """Importing the radiometric 2D histogram plotting function."""
    radiometric_2D_hist_plot = None
    if graphs:
        try:
            from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return radiometric_2D_hist_plot


def _ra_save_and_plot_results(
    output: list[RadiometricProfilesOutput],
    output_directory: Path,
    graphs_func: Callable,
    tag: str,
    plot_mode: str,
) -> tuple[Path, Path]:
    """Save Radiometric Analysis results to netCDF and plot graphs if required.

    Parameters
    ----------
    output : list[RadiometricProfilesOutput]
        radiometric profiles output from the radiometric analysis
    output_directory : Path
        Path to the output directory
    graphs_func : Callable
        radiometric 2D histogram plot function or None if graphs are not required
    tag : str
        tag referring to the kind of radiometric analysis performed
    plot_mode : str
        plot mode to be used for the graphs, min or mean

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    sct_logger.info("Saving results to netCDF...")

    kpi_file = output_directory.joinpath("radiometry_statistics.csv")
    stats_df = radiometric_statistical_analysis_to_df(data=output)
    stats_df.to_csv(kpi_file, index=False)
    netcdf_file = radiometric_profiles_to_netcdf(data=output, out_path=output_directory, tag=tag)
    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        for item in output:
            assert item.general_info.polarization is not None
            graphs_func(
                data=item,
                out_dir=output_directory,
                title=f"{tag.upper()} Profiles {item.general_info.channel}",
                plot_mode=plot_mode,
            )
    return netcdf_file, kpi_file
