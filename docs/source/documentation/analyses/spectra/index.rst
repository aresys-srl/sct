.. _sct_spectra:

Spectral Analysis
=================

.. toctree::
    :hidden:
    :maxdepth: 2

    config
    usage

This feature let the user compute the spectral analysis on SLC products. Two implementations of the spectral analysis are available:

- **Point Target**: computing the absolute and phase spectra at each visible target location
- **Distributed**: computing the spectral amplitude on bursts or azimuth blocks of the input product

The *Point Target Spectral Analysis* obviously requires a point target file to be provided in order to properly run the analysis.

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_spectra_config>` for a detailed description of the available parameters.
