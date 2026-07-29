---
icon: lucide/package-open
title: "Plugins"
tags:
    - plugins
    - architecture
    - input products
    - analyses
---

# SCT Plugins

SCT uses a **plugin-based architecture** to decouple core framework logic from
product-specific and analysis-specific implementations. Two distinct plugin types
are supported, each discovered through its own entry point namespace.

## Input Product Format Plugins

These plugins handle the **reading and parsing** of specific SAR product formats
(e.g., Sentinel-1, ICEYE, SAOCOM). Each plugin implements the
``sct.plugins.protocols.InputProductPluginProtocol`` and registers itself under
the ``sct.input_products`` entry point namespace.

Input product plugins provide:

- A **detector** to recognise the product format from a file path.
- A **manager class** that exposes the product data through the standard
  ``SCTInputProduct`` protocol.
- An optional **Absolute Localization Error (ALE) corrector**.

> :lucide-circle-chevron-right: Refer to [product format plugins](format_plugins.md) for details.

## Analysis Plugins

These plugins implement **quality analysis algorithms** (e.g., Point Target,
Radiometric, Spectral). Each plugin implements the
``sct.plugins.protocols.AnalysisPluginProtocol`` and registers itself under
the ``sct.analyses`` entry point namespace.

Analysis plugins provide:

- A **CLI command** automatically attached to the ``sct`` CLI.
- An **analysis handler** bundling configuration, CLI and testing hooks.
- The core analysis logic.

> :lucide-circle-chevron-right: Refer to [analysis plugins](analysis_plugins.md) for details.

## Discovery Mechanism

Both plugin types are discovered at runtime using
[stevedore](https://docs.openstack.org/stevedore/), a library for loading plugins
from Python entry points.

```python title="Plugin discovery (conceptual)"
from stevedore import ExtensionManager

# Input product plugins
input_manager = ExtensionManager(
    namespace="sct.input_products",
    invoke_on_load=True,
    on_load_failure_callback=_on_load_failure,
)

# Analysis plugins
analysis_manager = ExtensionManager(
    namespace="sct.analyses",
    invoke_on_load=True,
    on_load_failure_callback=_on_load_failure,
)
```

The core SCT framework never imports plugin packages directly — all interaction
goes through the protocols defined in ``sct.plugins.protocols``.

## Entry Point Namespaces

| Plugin Type | Namespace | Protocol |
|---|---|---|
| Input Product Format | ``sct.input_products`` | ``InputProductPluginProtocol`` |
| Analysis | ``sct.analyses`` | ``AnalysisPluginProtocol`` |

## Plugin Documentation

Each plugin is distributed as an independent Python package with its own
documentation. The official plugins documentation site collects all available
plugins and their documentation.

> :lucide-circle-chevron-right: Visit the [plugins documentation site](https://opensource.aresys.it/sct_plugins/)
> for the complete list of available input product and analysis plugins.
