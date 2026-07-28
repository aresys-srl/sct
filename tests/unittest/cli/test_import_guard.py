# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Import guard: ensure ``import sct`` and core CLI commands do not pull in heavy packages.

The following operations must NOT import ``numpy``, ``scipy``, ``pandas``,
``netCDF4``, any ``perseo`` sub-package, or any analysis implementation module
(``main``, ``cli``, ``config``, ``testing``):

- ``import sct``
- building the CLI app (``from sct.cli.cli import app``)
- ``sct --help``
- ``sct --version``

NOTE: ``sct info`` is NOT covered here because it currently loads input-product
plugins (via ``get_available_plugins``), which pulls in ``perseo``.  Fixing that
is a separate task.

Each test runs in a subprocess to guarantee a clean interpreter state.
"""

import subprocess
import sys
import textwrap

_SCRIPT = textwrap.dedent("""\
    import sys

    # --- prohibited modules ------------------------------------------------
    HEAVY: set[str] = {"numpy", "scipy", "pandas", "netCDF4"}

    ANALYSIS_IMPLS: set[str] = {
        f"sct.analyses.{d}.{s}"
        for d in ("point_target", "radiometry", "spectra",
                  "interferometry", "ambiguity_ratio", "elevation_notch")
        for s in ("main", "cli", "config", "testing")
    }

    def prohibited(loaded: set[str]) -> set[str]:
        bad: set[str] = set()
        for mod in loaded:
            if mod in HEAVY or mod.startswith("perseo") or mod in ANALYSIS_IMPLS:
                bad.add(mod)
        return bad

    # ---- step 1: import sct ------------------------------------------------
    import sct  # noqa: F811
    phase1 = set(sys.modules)
    bad1 = prohibited(phase1)

    # ---- step 2: build the CLI app -----------------------------------------
    from sct.cli.cli import app  # noqa: F811
    phase2 = set(sys.modules)
    bad2 = prohibited(phase2)

    # ---- step 3: run --help -------------------------------------------------
    try:
        app.main(["--help"], standalone_mode=False)
    except SystemExit:
        pass
    phase3 = set(sys.modules)
    bad3 = prohibited(phase3)

    # ---- step 4: run --version ----------------------------------------------
    try:
        app.main(["--version"], standalone_mode=False)
    except SystemExit:
        pass
    phase4 = set(sys.modules)
    bad4 = prohibited(phase4)

    all_bad = bad1 | bad2 | bad3 | bad4
    if all_bad:
        for mod in sorted(all_bad):
            label = ""
            if mod in bad1:
                label += " phase1(import sct)"
            if mod in bad2:
                label += " phase2(app build)"
            if mod in bad3:
                label += " phase3(--help)"
            if mod in bad4:
                label += " phase4(--version)"
            print(f"FAIL: {mod}{label}", file=sys.stderr)
        sys.exit(1)

    print("OK: no prohibited modules loaded")
    sys.exit(0)
""")


def test_core_cli_imports_no_heavy_packages() -> None:
    result = subprocess.run(
        [sys.executable, "-c", _SCRIPT],
        capture_output=True,
        text=True,
        timeout=30,
    )
    print(result.stdout, end="")
    if result.stderr:
        print("stderr:", result.stderr, end="")
    assert result.returncode == 0, f"Import guard violation (exit code {result.returncode})"
