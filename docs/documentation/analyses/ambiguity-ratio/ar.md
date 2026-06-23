---
icon: lucide/test-tube-diagonal
title: "Analysis"
tags:
    - ambiguity ratio analysis
    - ptar
    - analysis
---

# Point Target Ambiguity Ratio Analysis { #ptar data-toc-label="Ambiguity Ratio Analysis" }

This feature let the user compute the ratio between the signal and its left and right ambiguities, if captured by the
SAR acquisition.

Currently, only the **Point Target Ambiguity Ratio** (PTAR) analysis is implemented, performing the computation at each
visible target location.

This analysis can be configured through the configuration file.  
Refer to the [configuration documentation](config.md) for a detailed description of the available parameters.

> :lucide-circle-chevron-right: An in-depth description of the core algorithms used for this analysis can be found in
[PERSEO-Quality documentation](https://aresys-srl.github.io/perseo/documentation/quality/analyses/ambiguity-ratio/).
