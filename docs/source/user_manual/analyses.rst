.. _sct_analyses:

Implemented Features and Analyses
=================================

Here is reported a list of implemented features and available analyses for SCT.

Point Target Analysis
---------------------

This features let the user compute a full point target analysis starting from a SAR product containing data recorded in
correspondence of calibration sites hosting passive or active corner reflectors to estimate the quality of the acquisition
based on several KPIs and measured parameters.

This feature consists of the following computation steps:

- `Impulse Response Function (IRF)`: measuring resolution, Peak-to-Side-Lobe-Ratio (PSLR), Integral-Side-Lobe-Ratio (ISLR) and
  Secondary-Side-Lobe-Ratio (SSLR) along range and azimuth directions
- `Radar Cross-Section (RCS)`: measuring radar cross-section and its error, peak phase error, clutter and Signal-to-Clutter Ratio (SCR)
- `Absolute Localization Errors (ALE)`: measuring absolute localization errors both along range and azimuth directions

An in-depth description of the core algorithm used for point target analysis computation can be found here.

.. seealso::

   This analysis can be heavily configured through the configuration file and deeply customized. To better understand the
   implications of changing specific parameters, refer to the :ref:`documentation about tool configuration <sct_config>`.


Radiometric Profiles
--------------------

This features let the user compute radiometric profiles along range and/or azimuth directions starting from any supported
SAR product.

An in-depth description of the core algorithm used for radiometric analysis profiles computation can be found here.

.. seealso::

   This analysis can be configured through the configuration file and deeply customized. To better understand the
   implications of changing specific parameters, refer to the :ref:`documentation about tool configuration <sct_config>`.
