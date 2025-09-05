# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test radiometric analysis script"""

from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot
from perseo_quality.radiometric_analysis.block_wise.support import radiometric_profiles_to_netcdf

from sct.analyses import radiometric_analysis as ra
from sct.configuration.logger import ConsoleHandler, enable_quality_logger, sct_logger
from sct.configuration.sct_configuration import SCTConfiguration

# setup custom logger
enable_quality_logger()
sct_logger.addHandler(ConsoleHandler())
sct_logger.setLevel("INFO")


if __name__ == "__main__":
    # load custom config

    # path_to_config = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\prova.toml"
    path_to_config = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\eos04\config.toml"
    config = SCTConfiguration.from_toml(path_to_config)
    # config.radiometric_analysis.base_config.profile_extraction_parameters.outlier_removal = False
    # config.radiometric_analysis.base_config.profile_extraction_parameters.smoothening_filter = False
    # config = config.radiometric_analysis

    output_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\eos"

    prod = r"C:\Users\giorgio.parma\Aresys_DATA\sct_data\eos04\L1B_GRD\244711611"
    output = ra.nesz_analysis(product_path=prod, config=config.radiometric_analysis)
    # output = ra.average_elevation_profile_analysis(product_path=prod, output_quantity=SARRadiometricQuantity.GAMMA_NOUGHT, config=config.radiometric_analysis)
    tag = "NESZ"
    mode = "min"

    sct_logger.info("Plotting Graphs...")
    for item in output:
        radiometric_2D_hist_plot(item, output_dir, plot_mode=mode)
        radiometric_profiles_to_netcdf(item, output_dir, tag)

    pass
