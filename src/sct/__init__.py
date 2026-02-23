# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: the Python SAR Calibration Tool for quality data analysis
--------------------------------------------------------------
"""

from importlib import resources as res

import sct.resources as res_folder

csv_template = res.files(res_folder).joinpath("calibration_targets_external_source_template.csv")

__version__ = "2.0.9"
