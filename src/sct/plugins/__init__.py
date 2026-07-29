# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""SCT plugins manager (input products and analyses).

Plugin discovery is performed lazily and memoized on first use, so importing this
package (and ``import sct``) does not trigger loading of any plugin implementation.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def get_available_product_format_plugins() -> list:
    """Return the list of installed input-product plugins (discovered once, cached)."""
    from sct.plugins.loader import import_input_product_plugins

    return import_input_product_plugins()


@lru_cache(maxsize=1)
def get_available_analyses_plugins() -> list:
    """Return the list of installed analyses plugins (discovered once, cached)."""
    from sct.plugins.loader import import_analysis_plugins

    return import_analysis_plugins()
