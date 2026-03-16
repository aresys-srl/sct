---
icon: lucide/test-tube-diagonal
title: "Analysis"
tags:
    - interferometric analysis
    - analysis
---

# Interferometric Analysis { #interf data-toc-label="Interferometric Analysis" }

This feature let the user compute and plot the coherence (absolute and phase histograms and map) of an interferogram between
two co-registered products.

This analysis can be performed starting from:

- an interferogram product
- two co-registered products
- a coherence map product (coherence histograms are plotted)

!!! warning "Product Format"

    The interferometric analysis feature is limited to **Aresys internal SAR product format**.

This analysis can be configured through the configuration file.  
Refer to the [configuration documentation](config.md) for a detailed description of the available parameters.

> :lucide-circle-chevron-right: An in-depth description of the core algorithms used for this analysis can be found in
[PERSEO-Quality documentation](http://intranet.aresys.it/sardashboard/develop/perseo/quality/docs/latest/documentation/interferometric_analysis_doc.html).
