# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Analysis implementation
-----------------------
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig
from sct.analyses.point_target.core import sct_point_target_analysis_with_corrections
from sct.configuration.logger import sct_logger


def full_point_target_analysis(
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    external_orbit: Path | None,
    external_corrections_product: Path | None,
    config: SCTPointTargetAnalysisConfig | None,
    graphs: bool,
) -> Path:
    """Full implementation of Point Target Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    point_target_source : Path
        Path to the point target source file
    output_directory : Path
        Path to the output directory
    external_orbit : Path | None
        Path to the external orbit file, if any
    external_corrections_product : Path | None
        Path to the external corrections product, if any
    config : SCTPointTargetAnalysisConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation

    Returns
    -------
    Path
        Path to the CSV file containing the point target analysis results
    """
    graphs_func = _import_pta_graphs_func(graphs)
    results, graphs_data = sct_point_target_analysis_with_corrections(
        product_path=product,
        external_target_source=point_target_source,
        external_orbit_path=external_orbit,
        external_corrections_product=external_corrections_product,
        config=config,
    )
    results_filename = output_directory.joinpath("point_target_analysis_results.csv")
    results.to_csv(results_filename, index=False)
    if graphs_func is not None:
        sct_logger.info("Plotting graphs...")
        graphs_out_dir = output_directory.joinpath("graphs")
        graphs_out_dir.mkdir(exist_ok=True)
        graphs_func(graphs_data=graphs_data, results_df=results, output_dir=graphs_out_dir)
    return results_filename


def _import_pta_graphs_func(graphs: bool) -> Callable | None:
    """Importing the point target analysis plotting function."""
    point_target_graphs_generation = None
    if graphs:
        try:
            from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return point_target_graphs_generation
