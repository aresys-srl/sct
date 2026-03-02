.. _sct_interf:

Interferometric Analysis
========================

.. toctree::
    :hidden:
    :maxdepth: 2

    config
    usage

This feature let the user compute and plot the coherence (absolute and phase histograms and map) of an interferogram between
two co-registered products.

This analysis can be performed starting from:

- an interferogram product
- two co-registered products
- a coherence map product (coherence histograms are plotted)

.. note::

    The interferometric analysis feature is limited to **Aresys internal SAR product format**.

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_interf_config>` for a detailed description of the available parameters.
