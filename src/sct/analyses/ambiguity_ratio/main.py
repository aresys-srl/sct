# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Ambiguity Ratio Analysis implementation."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig
from sct.analyses.ambiguity_ratio.core.analysis import sct_point_target_ambiguity_ratio_analysis
from sct.configuration.logger import sct_logger


def full_pt_ambiguity_ratio_analysis(
    product: Path,
    point_target_source: Path,
    output_directory: Path,
    config: SCTTargetAmbiguityRatioConfig | None,
    graphs: bool,
) -> None:
    """Full implementation of Point Target Ambiguity Ratio Analysis.

    Parameters
    ----------
    product : Path
        Path to the product to be analyzed
    point_target_source : Path
        Path to the point target source file
    output_directory : Path
        Path to the output directory
    config : SCTTargetAmbiguityRatioConfig | None
        analysis configuration parameters, if needed
    graphs : bool
        flag to enable graphs generation
    """
    graphs_func = _import_ptar_graphs_func(graphs)
    output = sct_point_target_ambiguity_ratio_analysis(
        product_path=product,
        external_target_source=point_target_source,
        config=config,
    )

    if graphs_func is not None:
        sct_logger.info("Generating graphs...")
        output_graphs_dir = output_directory.joinpath("graphs")
        output_graphs_dir.mkdir(exist_ok=True)
        graphs_func(data=output, output_dir=output_graphs_dir)


def _import_ptar_graphs_func(graphs: bool) -> Callable | None:
    """Importing the target ambiguity ratio analysis graphs plotting function."""
    ambiguities_graphs = None
    if graphs:
        try:
            from perseo_quality.tar_analysis.graphical_output import ambiguities_graphs
        except ImportError as err:
            sct_logger.critical(
                'Cannot generate graphical output: install graphs requirements "pip install sct[graphs]"'
            )
            raise ImportError from err
    return ambiguities_graphs
