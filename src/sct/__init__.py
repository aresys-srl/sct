# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: the Python SAR Calibration Tool for quality data analysis
--------------------------------------------------------------
"""

import pkgutil
from importlib import import_module
from importlib import resources as res

import sct.resources as res_folder

csv_template = res.files(res_folder).joinpath("calibration_targets_external_source_template.csv")

sct_discovered_plugins = {name: import_module(name) for _, name, _ in pkgutil.iter_modules() if name.startswith("sct_")}

__version__ = "2.0.3"
