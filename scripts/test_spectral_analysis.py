# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test spectral analysis script"""

import logging

import arepyextras.quality.core.custom_logger as clg
from arepyextras.quality.interferometric_analysis.graphical_output import generate_coherence_graphs
from arepyextras.quality.interferometric_analysis.support import coherence_histograms_to_netcdf

from sct.analyses.spectral_analysis import sct_point_target_spectral_analysis
from sct.configuration.sct_configuration import SCTSpectralAnalysisConfig
from arepyextras.quality.spectral_analysis.graphical_output import spectral_graphs

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())

if __name__ == '__main__':
    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\novasar1\NovaSAR_01_38993_slc_11_221103_004941_HH"
    targets = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\novasar1\PointTargets_File__NOVASAR__surat_basin.xml"
    out_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"
    config = SCTSpectralAnalysisConfig()
    output = sct_point_target_spectral_analysis(
        product_path=prod,
        external_target_source=targets,
        config=config
    )
    spectral_graphs(data=output, output_dir=out_dir, graph_type="POINT")
