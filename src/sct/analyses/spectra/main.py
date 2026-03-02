# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis implementation
-----------------------
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from perseo_quality.spectral_analysis.support import spectral_analysis_profiles_to_netcdf

from sct.analyses.spectra.config import SCTSpectralAnalysisConfig
from sct.analyses.spectra.core import sct_distributed_spectral_analysis, sct_point_target_spectral_analysis
from sct.configuration.logger import sct_logger


def full_spectral_analysis(
    product: Path,
    point_target_source: Path | None,
    output_directory: Path,
    config: SCTSpectralAnalysisConfig | None,
    graphs: bool,
) -> Path:
    """Full implementation of Spectral Analysis, both distributed and point target.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    point_target_source : Path | None
        Path to the point target source file, if not provided the analysis will be a Distributed Spectral Analysis
    output_directory : Path
        Path to the output directory
    config : SCTSpectralAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the results
    """
    graphs_func = _import_spectral_graphs_func(graphs)
    if point_target_source is not None:
        output = sct_point_target_spectral_analysis(
            product_path=product,
            external_target_source=point_target_source,
            config=config,
        )
    else:
        output = sct_distributed_spectral_analysis(
            product_path=product,
            config=config,
        )
    sct_logger.info("Saving results to NetCDF...")
    netcdf_file = spectral_analysis_profiles_to_netcdf(data=output, out_path=output_directory)

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        output_graphs_dir = output_directory.joinpath("graphs")
        output_graphs_dir.mkdir(exist_ok=True)
        graphs_func(data=output, output_dir=output_graphs_dir)

    return netcdf_file


def _import_spectral_graphs_func(graphs: bool) -> Callable | None:
    """Importing the spectral analysis graphs plotting function."""
    spectral_graphs = None
    if graphs:
        try:
            from perseo_quality.spectral_analysis.graphical_output import spectral_graphs
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return spectral_graphs
