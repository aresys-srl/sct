# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Input product plugins manager."""

from sct.plugins.loader import import_input_product_plugins

available_plugins = import_input_product_plugins()
