# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test radiometric analysis script"""

import logging
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
from arepyextras.quality.core.generic_dataclasses import SARRadiometricQuantity
from arepyextras.quality.radiometric_analysis.graphical_output import radiometric_2D_hist_plot
from arepyextras.quality.radiometric_analysis.support import radiometric_profiles_to_netcdf

from sct.analyses import radiometric_analysis as ra
from sct.configuration.sct_configuration import SCTConfiguration

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())


if __name__ == "__main__":
    # load custom config

    # path_to_config = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\prova.toml"
    path_to_config = r"C:\ARESYS_PROJ_GITHUB\sct_e2e_tests\dataset\novasar\config.toml"
    config = SCTConfiguration.from_toml(path_to_config)
    # config.radiometric_analysis.base_config.input_quantity = SARRadiometricQuantity.BETA_NOUGHT
    # config.radiometric_analysis.base_config.profile_extraction_parameters.outlier_removal = False
    # config.radiometric_analysis.base_config.profile_extraction_parameters.smoothening_filter = False
    # config = config.radiometric_analysis

    output_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"

    prod = r"C:\ARESYS_PROJ_GITHUB\sct_e2e_tests\dataset\sentinel\S1A_IW_SLC__1SDH_20230404T184811_20230404T184841_047950_05C340_1EA0.SAFE"
    output = ra.nesz_analysis(product_path=prod)
    # output = ra.average_elevation_profile_analysis(product_path=prod, output_quantity=SARRadiometricQuantity.GAMMA_NOUGHT, config=config)
    tag = "NESZ"
    mode = "min"

    for item in output:
        radiometric_2D_hist_plot(item, output_dir, plot_mode=mode)
        radiometric_profiles_to_netcdf(item, output_dir, tag)

    pass
