# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test PTAR analysis script"""

from arepyextras.quality.target_ambiguity_ratio_analysis.graphical_output import ambiguities_graphs

from sct.analyses.ambiguity_ratio_analysis import sct_point_target_ambiguity_ratio_analysis
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTTargetAmbiguityRatioConfig

# setup custom logger
enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")

if __name__ == "__main__":
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\SLC_23.SAFE"
    targets = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\surat_basin_data.csv"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTTargetAmbiguityRatioConfig()
    output = sct_point_target_ambiguity_ratio_analysis(product_path=prod, external_target_source=targets, config=config)
    sct_logger.info("Plotting Graphs...")
    ambiguities_graphs(data=output, output_dir=out_dir, graph_type="PTAR")
