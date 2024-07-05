# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test radiometric analysis script"""

import logging

import arepyextras.quality.core.custom_logger as clg
from arepyextras.quality.interferometric_analysis.graphical_output import generate_coherence_graphs
from arepyextras.quality.interferometric_analysis.support import coherence_histograms_to_netcdf

from sct.analyses import interferometric_analysis as interf
from sct.configuration.sct_configuration import SCTInterferometricAnalysisConfig

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())

if __name__ == "__main__":
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\quality_data\interferometry\S1A_IW_SLC__1SDH_20240205T113611_20240205T113638_052423_065701_FDAB_PF_RORB_Cor_SCI_Mrg"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTInterferometricAnalysisConfig()
    config.base_config.enable_coherence_computation = True

    output = interf.interferometric_coherence_analysis(product_path=prod, config=config)
    for out in output:
        generate_coherence_graphs(out, output_dir=out_dir, mode="magnitude")
        generate_coherence_graphs(out, output_dir=out_dir, mode="phase")
        coherence_histograms_to_netcdf(out, output_dir=out_dir)
