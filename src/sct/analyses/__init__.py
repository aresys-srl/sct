# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
SCT - Implemented Analyses
--------------------------
"""

from __future__ import annotations


def load_analyses() -> None:
    """Loading all analyses defined in this package module"""
    import importlib
    import pkgutil
    from pathlib import Path

    package_path = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(package_path)]):
        if module_info.ispkg:
            importlib.import_module(f"{__name__}.{module_info.name}")
