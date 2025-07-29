# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test spectral analysis script"""

from sct.analyses.spectral_analysis import sct_point_target_spectral_analysis
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTSpectralAnalysisConfig
from arepyextras.quality.spectral_analysis.graphical_output import spectral_graphs

# setup custom logger
enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")


if __name__ == '__main__':
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\SLC_23.SAFE"
    targets = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\sentinel1\surat_basin_data.csv"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTSpectralAnalysisConfig()
    output = sct_point_target_spectral_analysis(
        product_path=prod,
        external_target_source=targets,
        config=config
    )
    sct_logger.info("Plotting Graphs...")
    spectral_graphs(data=output, output_dir=out_dir, graph_type="POINT")
