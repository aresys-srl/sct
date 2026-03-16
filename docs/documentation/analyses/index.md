---
icon: lucide/flask-conical
tags:
    - analysis
---

# Analyses and Features { #analyses data-toc-label="Analyses and Features" }

Here is reported a list of implemented features and available analyses for SCT:

<div class="result" markdown>

:lucide-crosshair:{ .lg .middle } [__Point Target Analysis__](point-target/pt.md#pta){ data-preview }

:lucide-signal:{ .lg .middle } [__Radiometric Analysis__ (NESZ, Average Elevation Profiles, Scalloping)](radiometry/rad.md#rad){ data-preview }

:lucide-git-branch:{ .lg .middle } [__Interferometric Analysis__](interferometry/interf.md#interf){ data-preview }

:lucide-ghost:{ .lg .middle } [__Spectral Analysis__](spectra/spectra.md#spectra){ data-preview }

:lucide-satellite-dish:{ .lg .middle } [__Elevation Notch Analysis__](notch/notch.md#notch){ data-preview }

:lucide-ratio:{ .lg .middle } [__Point Target Ambiguity Ratio (PTAR)__](ambiguity-ratio/ar.md#ptar){ data-preview }

</div>

The SCT framework uses a **plugin-based architecture** for analyses and all analyses are automatically discovered and
registered at runtime.

## Architecture Summary

Each analysis:

1. Lives under `#!text sct/analyses/<analysis_name>/`
2. Registers itself in its 🐍 ``__init__.py``
3. Is auto-loaded by ``sct.analyses.load_analyses``
4. Its CLI command is attached to the root ``sct.cli.cli`` CLI group

```title="Directory Structure Example"
📁 sct/
    📁 analyses/
        🐍 __init__.py
        📁 <analysis_name>/
            🐍 __init__.py
            🐍 cli.py
            🐍 main.py
            🐍 config.py
```

Analyses are automatically discovered and registered at runtime using function:

::: sct.analyses.load_analyses
    options:
        show_root_heading: true
        show_root_full_path: false
        show_source: true

## Analysis documentation

Each analysis documentation is organized as follows:

**<mark>&lt;analysis_name&gt;</mark>**

- **Analysis description**: overview of the analysis, methodology, and intended use cases.
- **Configuration description**: detailed explanation of available configuration options and parameters.
- **Usage**: usage description of the implemented analysis, calling the functionalities from CLI and Python API.
- **API**: detailed description of the implemented python API, including the available functions and classes.
