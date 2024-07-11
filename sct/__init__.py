# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: the Python SAR Calibration Tool for quality data analysis
--------------------------------------------------------------
"""
from importlib import resources as res

from . import resources

config_schema = res.files(resources).joinpath("configuration_schema.json")
csv_template = res.files(resources).joinpath("calibration_targets_external_source_template.csv")
calibration_sites_registry_schema = res.files(resources).joinpath("known_calibration_sites_registry_schema.json")

__version__ = "1.0.1"
