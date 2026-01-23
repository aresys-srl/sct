# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test radiometric analysis script"""

from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs
from perseo_quality.interferometric_analysis.support import coherence_histograms_to_netcdf

from sct.analyses import interferometric_analysis as interf
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTInterferometricAnalysisConfig

# setup custom logger
enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")


if __name__ == "__main__":
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\interferometry\PF_Cor_SCI"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTInterferometricAnalysisConfig()
    config.base_config.enable_coherence_computation = True

    output = interf.interferometric_coherence_analysis(product_path=prod, config=config)
    coherence_histograms_to_netcdf(output, output_dir=out_dir)
    sct_logger.info("Plotting Graphs...")
    for out in output:
        generate_coherence_graphs(out, output_dir=out_dir, mode="magnitude")
        generate_coherence_graphs(out, output_dir=out_dir, mode="phase")
