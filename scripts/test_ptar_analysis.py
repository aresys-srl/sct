# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test PTAR analysis script"""

import logging

import arepyextras.quality.core.custom_logger as clg
from sct.configuration.sct_configuration import SCTTargetAmbiguityRatioConfig
from sct.analyses.ambiguity_ratio_analysis import sct_point_target_ambiguity_ratio_analysis
from arepyextras.quality.target_ambiguity_ratio_analysis.graphical_output import ambiguities_graphs

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())

if __name__ == '__main__':
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\SLC_23.SAFE"
    targets = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\surat_basin_data.csv"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTTargetAmbiguityRatioConfig()
    output = sct_point_target_ambiguity_ratio_analysis(
        product_path=prod,
        external_target_source=targets,
        config=config
    )
    ambiguities_graphs(data=output, output_dir=out_dir, graph_type="PTAR")
