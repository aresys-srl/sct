# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Default analyses bundled with SCT.

Each analysis is exposed as an SCT analysis plugin through the ``sct.analyses``
entry-point namespace and discovered lazily at runtime (see
:mod:`sct.core.registry`). Nothing is imported at package import time so that
``import sct`` stays lightweight.
"""
