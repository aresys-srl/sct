# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Orchestration Features - Easily importable complete workflow for all analyses
---------------------------------------------------------------------------------
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

import sct.analyses.point_target_analysis as pta
import sct.analyses.radiometric_analysis as ra
from sct.configuration.logger import sct_logger
from sct.configuration.sct_configuration import SCTConfiguration


def full_point_target_analysis_implementation(
    product: Path,
    external_orbit: Path | None,
    external_corrections_product: Path | None,
    point_target_source: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
) -> Path:
    """Full implementation of Point Target Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    external_orbit : Path | None
        Path to the external orbit file, if any
    external_corrections_product : Path | None
        Path to the external corrections product, if any
    point_target_source : Path
        Path to the point target source file
    output_directory : Path
        Path to the output directory
    config : SCTConfiguration
        configuration parameters
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required

    Returns
    -------
    Path
        Path to the CSV file containing the point target analysis results
    """
    results, graphs_data = pta.point_target_analysis_with_corrections(
        product_path=product,
        external_orbit_path=external_orbit,
        external_target_source=point_target_source,
        external_corrections_product=external_corrections_product,
        config=config.point_target_analysis,
    )
    results_filename = output_directory.joinpath("point_target_analysis_results.csv")
    results.to_csv(results_filename, index=False)
    if graphs_func is not None:
        sct_logger.info("Plotting graphs...")
        graphs_out_dir = output_directory.joinpath("graphs")
        graphs_out_dir.mkdir(exist_ok=True)
        graphs_func(graphs_data=graphs_data, results_df=results, output_dir=graphs_out_dir)
    return results_filename


def full_nesz_implementation_core(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
) -> tuple[Path, Path]:
    """Full implementation of Noise Equivalent Sigma-Zero (NESZ) Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_directory : Path
        Path to the output directory
    config : SCTConfiguration
        configuration parameters
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    output = ra.nesz_analysis(product_path=product, config=config.radiometric_analysis)
    return _ra_save_and_plot_results(
        output=output,
        output_directory=output_directory,
        radiometric_2d_hist_plot=graphs_func,
        tag="NESZ",
    )


def full_average_elevation_profiles_implementation_core(
    product: Path,
    output_radiometric_quantity: SARRadiometricQuantity,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
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
    config : SCTConfiguration
        configuration parameters
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    output = ra.average_elevation_profile_analysis(
        product_path=product,
        output_quantity=output_radiometric_quantity,
        config=config.radiometric_analysis,
    )
    return _ra_save_and_plot_results(
        output=output,
        output_directory=output_directory,
        radiometric_2d_hist_plot=graphs_func,
        tag=f"AVERAGE_{output_radiometric_quantity.name}",
    )


def full_scalloping_implementation_core(
    product: Path,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
) -> tuple[Path, Path]:
    """Full implementation of Scalloping Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    output_directory : Path
        Path to the output directory
    config : SCTConfiguration
        configuration parameters
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    output = ra.scalloping_analysis(product_path=product, config=config.radiometric_analysis)
    return _ra_save_and_plot_results(
        output=output,
        output_directory=output_directory,
        radiometric_2d_hist_plot=graphs_func,
        tag="SCALLOPING",
    )


def _ra_save_and_plot_results(
    output: list[RadiometricProfilesOutput],
    output_directory: Path,
    radiometric_2d_hist_plot: Callable,
    tag: str,
) -> tuple[Path, Path]:
    """Save Radiometric Analysis results to netCDF and plot graphs if required.

    Parameters
    ----------
    output : list[RadiometricProfilesOutput]
        radiometric profiles output from the radiometric analysis
    output_directory : Path
        Path to the output directory
    radiometric_2d_hist_plot : Callable
        radiometric 2D histogram plot function or None if graphs are not required
    tag : str
        tag referring to the kind of radiometric analysis performed

    Returns
    -------
    Path
        Path to the NetCDF file containing the radiometric profiles
    Path
        Path to the CSV file containing the radiometric statistics
    """
    if radiometric_2d_hist_plot is not None:
        sct_logger.info("Saving results to netCDF and plotting graphs...")
    else:
        sct_logger.info("Saving results to netCDF format...")

    kpi_file = output_directory.joinpath("radiometry_statistics.csv")
    stats_df = radiometric_statistical_analysis_to_df(data=output)
    stats_df.to_csv(kpi_file, index=False)
    netcdf_file = radiometric_profiles_to_netcdf(data=output, out_path=output_directory, tag=tag)
    if radiometric_2d_hist_plot is not None:
        for item in output:
            assert item.general_info.polarization is not None
            radiometric_2d_hist_plot(
                data=item,
                out_dir=output_directory,
                title=f"{tag.upper()} Profiles {item.general_info.channel}",
            )
    return netcdf_file, kpi_file
