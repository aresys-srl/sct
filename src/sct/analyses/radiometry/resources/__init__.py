# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Radiometric Analysis resources"""

from importlib import resources

config_schema = resources.files(__package__).joinpath("config_schema.json")
