# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis implementation
-----------------------
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from perseo_quality.elevation_notch_analysis.support import elevation_notch_profiles_to_netcdf

from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig
from sct.analyses.elevation_notch.core import sct_elevation_notch_analysis
from sct.configuration.logger import sct_logger


def full_elevation_notch_analysis(
    product: Path,
    antenna_pattern: Path | None,
    output_directory: Path,
    config: SCTElevationNotchAnalysisConfig | None,
    graphs: bool,
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
    config : SCTElevationNotchAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the results
    """
    graphs_func = _import_notch_graphs_func(graphs)
    output = sct_elevation_notch_analysis(product_path=product, antenna_pattern_file=antenna_pattern, config=config)
    sct_logger.info("Saving results to NetCDF...")
    netcdf_file = elevation_notch_profiles_to_netcdf(data=output, output_dir=output_directory)

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        output_graphs_dir = output_directory.joinpath("graphs")
        output_graphs_dir.mkdir(exist_ok=True)
        graphs_func(data=output, output_dir=output_graphs_dir)

    return netcdf_file


def _import_notch_graphs_func(graphs: bool) -> Callable | None:
    """Importing the elevation notch analysis graphs plotting function."""
    plot_elevation_notch_analysis = None
    if graphs:
        try:
            from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return plot_elevation_notch_analysis
