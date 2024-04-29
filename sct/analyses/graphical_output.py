# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Graphical output for implemented analyses
-----------------------------------------
"""

from __future__ import annotations

import logging
from pathlib import Path

import arepyextras.quality.point_targets_analysis.graphical_output as pta_go
import pandas as pd
from arepyextras.quality.point_targets_analysis.custom_dataclasses import PointTargetGraphicalData

# syncing with logger
log = logging.getLogger("quality_analysis")


def sct_pta_graphs(
    graphs_data: list[PointTargetGraphicalData], results_df: pd.DataFrame, output_dir: str | Path
) -> None:
    """Point Target Analysis output graphs.

    Parameters
    ----------
    graphs_data : list[PointTargetGraphicalData]
        graphs data for plotting results
    results_df : pd.DataFrame
        point target analysis results dataframe
    output_dir : str | Path
        path to output directory where to save the graphs
    """
    output_dir = Path(output_dir)

    for item in graphs_data:
        try:
            data_val = results_df.query("target_name == @item.target & channel == @item.channel").to_dict("records")[0]
            label = (
                f"target_{data_val['target_name']}_{data_val['swath']}_"
                + f"polarization_{data_val['polarization'].replace('/','')}"
            )
            pta_go.irf_graphs(
                data_graph=item.irf,
                data_values=data_val,
                label=label,
                out_dir=output_dir,
            )
            pta_go.rcs_graphs(
                data_graph=item.rcs,
                label=label,
                out_dir=output_dir,
            )
        except Exception:
            log.error(f"Could not create graph for {item.channel}, target {item.target} ...")
            continue
