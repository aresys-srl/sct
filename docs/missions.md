---
icon: lucide/satellite
title: "Missions & Sensors"
tags:
    - input products
    - missions
    - plugins
---

# Supported Missions and Products

The list of supported product types, a.k.a. missions and formats, that can be used as inputs for the SCT analyses
features is herein reported:

- **Sentinel-1**
- **ICEYE**
- **NovaSAR-1**
- **SAOCOM**
- **EOS-04**
- **COSMO SkyMed**
- **RADARSAT-2**
- **ENVISAT/ERS**

!!! note "Supported Products"

    Support for **L1 products only** (both L1-A and L1-B) for each of these formats is available.

## SCT Product Format Plugins

The SCT software itself **does not natively support any specific format** of Level 1 SAR products. Instead, it has been
designed to *abstract away the dependency on the input format*, relying solely on a generic Python protocol.
Once this protocol is satisfied, it enables the execution of all implemented analyses regardless of the type of input
product.

To handle the implementation of the methods and properties defined by the protocol, *custom Python packages* are used,
each dedicated to a particular sensor or format. These packages, **managed as plugins** by the software, are solely
responsible for assembling the information read from the product in its specific format, processing it, and ensuring that
all the functionalities required by the protocol are implemented.

> :lucide-circle-chevron-right: Refer to the [plugins implementation documentation](format_plugins.md) for further information.

## Product Format Plugins Documentation

A dedicated documentation site has been created to explain the implementation of the protocol and the plugins and to list
all the supported sensors and formats.

> :lucide-circle-chevron-right: Refer to the [official plugins documentation](https://aresys-srl.github.io/sct_plugins/) for further information.
