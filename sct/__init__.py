# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: the Python SAR Calibration Tool for quality data analysis
--------------------------------------------------------------
"""
from importlib import resources as res

from . import resources

calibration_sites_db = res.files(resources).joinpath("calibration_sites_db", "calibration_sites.sqlite")
config_schema = res.files(resources).joinpath("configuration_schema.json")
csv_template = res.files(resources).joinpath("calibration_targets_external_source_template.csv")

__version__ = "1.0.0dev0"
