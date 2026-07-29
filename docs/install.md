---
icon: lucide/arrow-big-down-dash
title: "Install"
tags:
    - python
    - pip
    - install
---

# Installation

!!! note "Requirements"

    SCT requires a Python version **equal or higher than 3.11**.

To install SCT using ``pip``:

``` bash title="Recommended installation"
pip install sct[recommended]
```

This will install SCT together with the **recommended set of analysis plugins** (Point Target, Radiometric, Spectral,
Interferometry, Elevation Notch, Ambiguity Ratio), **graphing dependencies** and **web utilities**.

If you only need the core framework without the optional dependencies:

``` bash title="Minimal installation"
pip install sct
```

!!! tip "Virtual Environments"

    We recommend using a dedicated virtual environment to install the main SCT software.  
    This will ensure that the software is installed in a separate environment and avoids conflicts with other packages
    or dependencies.

## Optional dependency groups

| Extra            | Description                                    |
| ---------------- | ---------------------------------------------- |
| ``recommended``  | All analysis plugins, graphs and web utilities |
| ``analyses``     | All analysis plugins                           |
| ``graphs``       | Matplotlib and graphical output support        |
| ``web``          | Requests library for TEC map downloads         |
| ``localtesting`` | Test with local input product readers          |
| ``test``         | Testing framework (pytest, pytest-cov)         |
| ``dev``          | Development tools (ruff, pylint)               |
| ``doc``          | Documentation build tools                      |

## Plugins installation

SCT is designed to be extensible and several plugins to support different input products formats have been developed
and distributed as separate packages.

> :lucide-circle-chevron-right: Refer to the [official plugins documentation](https://opensource.aresys.it/sct_plugins/install/) for further information on how to install plugins.
