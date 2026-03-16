---
icon: lucide/plug-zap
title: "New plugin"
tags:
    - development
    - plugins
    - inputs
---

# Creating a New Format Plugin

SCT supports multiple satellite product formats through a **plugin-based architecture**.
Instead of embedding format-specific logic directly in the core library, input products are handled by **external plugin packages**
that implement a common interface.

An SCT input product plugin is a **separate Python package** that:

1. Implements the ``sct.plugins.protocols.InputProductPluginProtocol``.
2. Exposes the plugin class through a **Python entry point** in the ``sct.input_products`` namespace.
3. Is installed alongside SCT so it can be **automatically discovered**.

Once installed, SCT will detect the plugin at runtime and make it available to the analysis pipeline.

> :lucide-circle-chevron-right: Refer to the [official plugins documentation](http://intranet.aresys.it/sardashboard/develop/sct-plugins/docs/docs/latest/architecture/arch/) for further information on how plugins are structured and how to create new ones.
