# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT: test radiometric analysis script"""

import logging
from pathlib import Path

import arepyextras.quality.core.custom_logger as clg
from arepyextras.quality.radiometric_analysis.graphical_output import radiometric_2D_hist_plot

from sct.analyses import radiometric_analysis as ra
from sct.configuration.sct_configuration import SCTConfiguration

# setup custom logger
log = logging.getLogger("quality_analysis")
log.setLevel("INFO")
log.addHandler(clg.MyHandler())


if __name__ == "__main__":
    # load custom config

    # path_to_config = r"C:\Users\giorgio.parma\Desktop\temporary_outputs\prova.toml"
    # config = SCTConfiguration.from_toml(path_to_config)
    # config = config.radiometric_analysis

    output_dir = r"C:\Users\giorgio.parma\Desktop\temporary_outputs"

    prod = r"C:\Users\giorgio.parma\Desktop\sct_benchmarking\S1A_IW_SLC__1SSH_20190108T083240_20190108T083310_025383_02CF92_AB14.SAFE"
    output = ra.nesz_analysis(product_path=prod)

    for item in output:
        radiometric_2D_hist_plot(item, output_dir)

    pass
