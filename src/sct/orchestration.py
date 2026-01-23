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
from perseo_quality.elevation_notch_analysis.support import elevation_notch_profiles_to_netcdf
from perseo_quality.interferometric_analysis.support import coherence_histograms_to_netcdf
from perseo_quality.radiometric_analysis.block_wise.support import (
    radiometric_profiles_to_netcdf,
    radiometric_statistical_analysis_to_df,
)
from perseo_quality.radiometric_analysis.custom_dataclasses import RadiometricProfilesOutput

import sct.analyses.interferometric_analysis as interf
import sct.analyses.point_target_analysis as pta
import sct.analyses.radiometric_analysis as ra
from sct.analyses.elevation_notch import sct_elevation_notch_analysis
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


def full_nesz_implementation(
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
        graphs_func=graphs_func,
        tag="NESZ",
    )


def full_average_elevation_profiles_implementation(
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
        graphs_func=graphs_func,
        tag=f"AVERAGE_{output_radiometric_quantity.name}",
    )


def full_scalloping_implementation(
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
        graphs_func=graphs_func,
        tag="SCALLOPING",
    )


def full_interferometric_analysis_implementation(
    product: Path,
    product_2: Path | None,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
) -> None:
    """Full implementation of Interferometric Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    product_2 : Path | None
        Second co-registered product, must be provided if the first product is not an interferogram
    config : SCTConfiguration
        configuration parameters
    output_directory : Path
        Path to the output directory
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required
    """
    coherence_res = interf.interferometric_coherence_analysis(
        product_path=product,
        second_product_path=product_2,
        config=config.interferometric_analysis,
    )
    # TODO: edit PERSEO QUALITY to save all these in a single NetCDF file an return its path
    for res in coherence_res:
        coherence_histograms_to_netcdf(data=res, output_dir=output_directory)

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        for res in coherence_res:
            graphs_func(
                data=res,
                output_dir=output_directory,
                mode="magnitude",
                config=config.interferometric_analysis.base_config,
            )
            graphs_func(
                data=res,
                output_dir=output_directory,
                mode="phase",
                config=config.interferometric_analysis.base_config,
            )


def full_elevation_notch_analysis_implementation(
    product: Path,
    antenna_pattern: Path | None,
    output_directory: Path,
    config: SCTConfiguration,
    graphs_func: Callable | None,
) -> Path:
    """Full implementation of Elevation Notch Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    antenna_pattern : Path | None
        Path to the antenna pattern NetCDF file
    output_directory : Path
        Path to the output directory
    config : SCTConfiguration
        configuration parameters
    graphs_func : Callable | None
        graph plotting function or None if graphs are not required

    Returns
    -------
    Path
        Path to the NetCDF file containing the results
    """
    output = sct_elevation_notch_analysis(
        product_path=product, antenna_pattern_file=antenna_pattern, config=config.elevation_notch_analysis
    )
    sct_logger.info("Saving results to NetCDF...")
    netcdf_file = elevation_notch_profiles_to_netcdf(data=output, output_dir=output_directory)

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        output_graphs_dir = output_directory.joinpath("graphs")
        output_graphs_dir.mkdir(exist_ok=True)
        graphs_func(data=output, output_dir=output_graphs_dir)

    return netcdf_file


def _ra_save_and_plot_results(
    output: list[RadiometricProfilesOutput],
    output_directory: Path,
    graphs_func: Callable,
    tag: str,
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
            )
    return netcdf_file, kpi_file
