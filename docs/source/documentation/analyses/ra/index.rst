.. _sct_ra:

Radiometric Analysis
====================

.. toctree::
    :hidden:
    :maxdepth: 2

    config
    usage
    tutorial

This feature let the user compute *Radiometric Profiles* along range and/or azimuth directions starting from any supported
SAR product.

The implemented radiometric profiles are:

- **Noise Equivalent Sigma Zero** (NESZ)
- **Average Elevation Profiles** (i.e. Rain Forest Gamma Profiles)
- **Scalloping**

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be heavily configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_ra_config>` for a detailed description of the available parameters.
