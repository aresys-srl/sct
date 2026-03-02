.. _sct_pta:

Point Target Analysis
=====================

.. toctree::
    :hidden:
    :maxdepth: 2

    config
    pta_corrections
    usage
    tutorial

This feature let the user compute a full point target analysis starting from a SAR product containing data recorded in
correspondence of calibration sites hosting passive or active corner reflectors to estimate the quality of the acquisition
based on several KPIs and measured parameters.

This feature consists of the following computation steps:

- `Impulse Response Function (IRF)`: measuring resolution, Peak-to-Side-Lobe-Ratio (PSLR), Integral-Side-Lobe-Ratio (ISLR) and
  Secondary-Side-Lobe-Ratio (SSLR) along range and azimuth directions
- `Radar Cross-Section (RCS)`: measuring radar cross-section and its error, peak phase error, clutter and Signal-to-Clutter Ratio (SCR)
- `Absolute Localization Errors (ALE)`: measuring absolute localization errors both along range and azimuth directions

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be heavily configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_pta_config>` for a detailed description of the available parameters.

Geolocation Corrections
-----------------------

The Point Target Analysis can be performed using the following corrections:

- **Atmospheric Corrections**: ionospheric delay correction, tropospheric delay correction
- **Geodynamics Corrections**: solid Earth Tides correction, plate tectonics correction
- **Processing Corrections**: sensor specific processing corrections

Please refer to the :ref:`documentation about corrections<sct_pta_corrections>` for further information.
