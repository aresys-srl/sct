# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT Integration Tests - Utilities
---------------------------------
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity

from sct.configuration.logger import sct_logger
from sct.configuration.point_target_analysis_configuration import (
    IonosphericCorrectionsConf,
    TroposphericCorrectionsConf,
)
from sct.configuration.sct_configuration import (
    SCTConfiguration,
    SCTElevationNotchAnalysisConfig,
    SCTInterferometricAnalysisConfig,
)
from sct.orchestration import (
    full_average_elevation_profiles_implementation,
    full_elevation_notch_analysis_implementation,
    full_interferometric_analysis_implementation,
    full_nesz_implementation,
    full_point_target_analysis_implementation,
)
from sct.testing.utilities.common import SCTAnalyses, TestParams
from sct.testing.utilities.validation import (
    compare_elevation_notch_netcdf_with_tolerances,
    compare_interf_netcdf_with_tolerances,
    compare_pta_df_with_tolerances,
    validate_ra_results,
)


def api_testing(
    test_params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool = False
) -> None:
    """SCT API testing routine."""
    match test_params.analysis:
        case SCTAnalyses.POINT_TARGET:
            results = run_pta_api(params=test_params, output_dir=output_dir, config=config, graphs=graphs)
            # comparing dataframes differences to specific tolerances
            sct_logger.info("Validating results...")
            compare_pta_df_with_tolerances(ref=pd.read_csv(test_params.reference_output), current=pd.read_csv(results))
        case SCTAnalyses.NESZ:
            nc_results, kpi_results = run_nesz_api(
                params=test_params, output_dir=output_dir, config=config, graphs=graphs
            )
            # comparing dataframes and netcdf differences to specific tolerances
            sct_logger.info("Validating results...")
            validate_ra_results(
                reference_output=test_params.reference_output,
                current_nc_output=nc_results,
                current_kpi_stats=kpi_results,
            )
        case SCTAnalyses.RAIN_FOREST:
            nc_results, kpi_results = run_rain_forest_api(
                params=test_params, output_dir=output_dir, config=config, graphs=graphs
            )
            # comparing dataframes and netcdf differences to specific tolerances
            sct_logger.info("Validating results...")
            validate_ra_results(
                reference_output=test_params.reference_output,
                current_nc_output=nc_results,
                current_kpi_stats=kpi_results,
            )
        case SCTAnalyses.INTERFEROMETRY:
            results = run_interferometry_api(params=test_params, output_dir=output_dir, config=config, graphs=graphs)
            sct_logger.info("Validating results...")
            compare_interf_netcdf_with_tolerances(ref=test_params.reference_output, current=results)
        case SCTAnalyses.ELEVATION_NOTCH:
            results = run_elevation_notch_api(params=test_params, output_dir=output_dir, config=config, graphs=graphs)
            sct_logger.info("Validating results...")
            compare_elevation_notch_netcdf_with_tolerances(ref=test_params.reference_output, current=results)


def run_pta_api(params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool) -> pd.DataFrame:
    """Running SCT Point Target Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    pd.DataFrame
        results dataframe
    """
    if params.ionospheric_maps is not None:
        config.point_target_analysis.corrections.enable_ionospheric_correction = True
        config.point_target_analysis.corrections.ionosphere = IonosphericCorrectionsConf(
            maps_directory=params.ionospheric_maps,
            analysis_center=config.point_target_analysis.corrections.ionosphere.analysis_center,
        )
    if params.tropospheric_maps is not None:
        config.point_target_analysis.corrections.enable_tropospheric_correction = True
        config.point_target_analysis.corrections.troposphere = TroposphericCorrectionsConf(
            maps_directory=params.tropospheric_maps
        )
    point_target_graphs_generation = None
    if graphs:
        try:
            from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return full_point_target_analysis_implementation(
        product=params.product,
        external_orbit=params.external_orbit,
        external_corrections_product=params.external_corrections_product,
        point_target_source=params.targets,
        output_directory=output_dir,
        config=config,
        graphs_func=point_target_graphs_generation,
    )


def run_nesz_api(
    params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool
) -> tuple[Path, Path]:
    """Running SCT NESZ Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to output netcdf file
    Path
        path to the kpi statistics file
    """
    return full_nesz_implementation(
        product=params.product,
        output_directory=output_dir,
        config=config,
        graphs_func=_load_ra_graphs_func(graphs),
    )


def run_rain_forest_api(
    params: TestParams, output_dir: Path, config: SCTConfiguration | None, graphs: bool
) -> tuple[Path, Path]:
    """Running SCT Average Radiometric Profiles Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTConfiguration | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to output netcdf file
    Path
        path to the kpi statistics file
    """
    return full_average_elevation_profiles_implementation(
        product=params.product,
        output_radiometric_quantity=SARRadiometricQuantity.GAMMA_NOUGHT,
        output_directory=output_dir,
        config=config,
        graphs_func=_load_ra_graphs_func(graphs),
    )


def run_interferometry_api(
    params: TestParams, output_dir: Path, config: SCTInterferometricAnalysisConfig | None, graphs: bool
) -> Path:
    """Running SCT Interferometric Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTInterferometricAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to output netcdf file
    """
    generate_coherence_graphs = None
    if graphs:
        try:
            from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return full_interferometric_analysis_implementation(
        product=params.product if isinstance(params.product, Path) else params.product[0],
        product_2=params.product[1] if isinstance(params.product, list) else None,
        config=config,
        output_directory=output_dir,
        graphs_func=generate_coherence_graphs,
    )


def run_elevation_notch_api(
    params: TestParams, output_dir: Path, config: SCTElevationNotchAnalysisConfig | None, graphs: bool
) -> Path:
    """Running SCT Elevation Notch Analysis from API forwarding the inputs.

    Parameters
    ----------
    params : TestParams
        test parameters
    output_dir : Path
        output directory
    config : SCTElevationNotchAnalysisConfig | None
        configuration
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        path to output netcdf file
    """
    plot_elevation_notch_analysis = None
    if graphs:
        try:
            from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return full_elevation_notch_analysis_implementation(
        product=params.product,
        antenna_pattern=params.antenna_pattern,
        output_directory=output_dir,
        config=config,
        graphs_func=plot_elevation_notch_analysis,
    )


def _load_ra_graphs_func(graphs: bool) -> None:
    """Loading the radiometric 2D histogram plotting function."""
    radiometric_2D_hist_plot = None
    if graphs:
        try:
            from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
        except ImportError:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
    return radiometric_2D_hist_plot
