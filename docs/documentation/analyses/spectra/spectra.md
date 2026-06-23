---
icon: lucide/test-tube-diagonal
title: "Analysis"
tags:
    - spectral analysis
    - analysis
---

# Spectral Analysis { #spectra data-toc-label="Spectral Analysis" }

This feature let the user compute the spectral analysis on SLC products. Two implementations of the spectral analysis are available:

- **Point Target**: computing the absolute and phase spectra at each visible target location
- **Distributed**: computing the spectral amplitude on bursts or azimuth blocks of the input product

The *Point Target Spectral Analysis* obviously requires a point target file to be provided in order to properly run the analysis.

This analysis can be configured through the configuration file.  
Refer to the [configuration documentation](config.md) for a detailed description of the available parameters.

> :lucide-circle-chevron-right: An in-depth description of the core algorithms used for this analysis can be found in
[PERSEO-Quality documentation](https://aresys-srl.github.io/perseo/documentation/quality/analyses/spectra/).
