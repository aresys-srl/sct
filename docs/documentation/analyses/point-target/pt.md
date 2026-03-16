---
icon: lucide/test-tube-diagonal
title: "Analysis"
tags:
    - point target analysis
    - corrections
    - analysis
---

# Point Target Analysis { #pta data-toc-label="Point Target Analysis" }

This feature let the user compute a full point target analysis starting from a SAR product containing data recorded in
correspondence of calibration sites hosting passive or active corner reflectors to estimate the quality of the acquisition
based on several KPIs and measured parameters.

This feature consists of the following computation steps:

- ==Impulse Response Function (IRF)==: measuring resolution, Peak-to-Side-Lobe-Ratio (PSLR), Integral-Side-Lobe-Ratio (ISLR) and
  Secondary-Side-Lobe-Ratio (SSLR) along range and azimuth directions
- ==Radar Cross-Section (RCS)==: measuring radar cross-section and its error, peak phase error, clutter and Signal-to-Clutter Ratio (SCR)
- ==Absolute Localization Errors (ALE)==: measuring absolute localization errors both along range and azimuth directions

This analysis can be heavily configured through the configuration file and deeply customized.  
Refer to the [configuration documentation](config.md) for a detailed description of the available parameters.

> :lucide-circle-chevron-right: An in-depth description of the core algorithms used for this analysis can be found in
[PERSEO-Quality documentation](http://intranet.aresys.it/sardashboard/develop/perseo/quality/docs/latest/documentation/point_target_analysis_doc.html).

## Geolocation Corrections

The Point Target Analysis can be performed using the following corrections:

- **Atmospheric Corrections**: ionospheric delay correction, tropospheric delay correction
- **Geodynamics Corrections**: solid Earth Tides correction, plate tectonics correction
- **Processing Corrections**: sensor specific processing corrections

> :lucide-circle-chevron-right: Refer to the [documentation about corrections](corrections.md) for more details.
