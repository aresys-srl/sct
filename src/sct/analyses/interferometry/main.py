# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis implementation
-----------------------
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from perseo_quality.interferometric_analysis.support import coherence_histograms_to_netcdf

from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig
from sct.analyses.interferometry.core import sct_interferometric_coherence_analysis
from sct.configuration.logger import sct_logger


def full_interferometric_analysis(
    product: Path,
    product_2: Path | None,
    output_directory: Path,
    config: SCTInterferometricAnalysisConfig | None,
    graphs: bool,
) -> Path:
    """Full implementation of Interferometric Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    product_2 : Path | None
        Second co-registered product, must be provided if the first product is not an interferogram
    config : SCTInterferometricAnalysisConfig | None
        analysis configuration parameters, if needed
    output_directory : Path
        Path to the output directory
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the NetCDF file containing the results
    """
    graphs_func = _import_interf_graphs_func(graphs)
    coherence_res = sct_interferometric_coherence_analysis(
        product_path=product,
        second_product_path=product_2,
        config=config,
    )
    netcdf_file = coherence_histograms_to_netcdf(data=coherence_res, output_dir=output_directory)

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        for res in coherence_res:
            graphs_func(
                data=res,
                output_dir=output_directory,
                mode="magnitude",
                config=config.base_config,
            )
            graphs_func(
                data=res,
                output_dir=output_directory,
                mode="phase",
                config=config.base_config,
            )
    return netcdf_file


def _import_interf_graphs_func(graphs: bool) -> Callable | None:
    """Importing the interferometric analysis graphs plotting function."""
    generate_coherence_graphs = None
    if graphs:
        try:
            from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return generate_coherence_graphs
