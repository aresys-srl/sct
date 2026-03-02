.. _sct_ptar:

Target Ambiguity Ratio Analysis
===============================

.. toctree::
    :hidden:
    :maxdepth: 2

    config

This feature let the user compute the ratio between the signal and its left and right ambiguities, if captured by the
SAR acquisition.

Currently, only the **Point Target Ambiguity Ratio** (PTAR) analysis is implemented, performing the computation at each
visible target location.

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_ptar_config>` for a detailed description of the available parameters.
