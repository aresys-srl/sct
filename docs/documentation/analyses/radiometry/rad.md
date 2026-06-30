---
icon: lucide/test-tube-diagonal
title: "Analysis"
tags:
    - radiometric analysis
    - analysis
    - nesz
    - rain forest
    - radiometric profiles
    - scalloping
---

# Radiometric Analysis { #rad data-toc-label="Radiometric Analysis" }

This feature let the user compute *Radiometric Profiles* along range and/or azimuth directions starting from any supported
SAR product.

The implemented radiometric profiles are:

- **Noise Equivalent Sigma Zero** (NESZ)
- **Average Elevation Profiles** (i.e. Rain Forest Gamma Profiles)
- **Scalloping**

This analysis can be configured through the configuration file.  
Refer to the [configuration documentation](config.md) for a detailed description of the available parameters.

> :lucide-circle-chevron-right: An in-depth description of the core algorithms used for this analysis can be found in
[PERSEO-Quality documentation](https://opensource.aresys.it/perseo/documentation/quality/analyses/radiometry/).
