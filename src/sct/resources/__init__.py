# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT: resources
--------------
"""

from importlib import resources

config_schema = resources.files(__package__).joinpath("config_schema.json")
csv_template = resources.files(__package__).joinpath("calibration_targets_external_source_template.csv")
