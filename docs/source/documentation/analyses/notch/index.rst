Elevation Notch Analysis
========================

.. toctree::
    :hidden:
    :maxdepth: 2

    config
    usage

This feature let the user compute the actual antenna pointing of the sensor, estimating it directly from the SAR data,
accounting for the fact that the beam is generally steered toward a swath-dependent look angle rather than the antenna boresight.

This analysis let the user find the mis-pointing angle that best matches the measured SAR range profiles with the theoretical
**Antenna Elevation Pattern**, if provided.

An in-depth description of the core algorithms used for this analysis can be found in PERSEO-Quality documentation.

This analysis can be configured through the configuration file and deeply customized.
Refer to the :ref:`configuration documentation<sct_notch_config>` for a detailed description of the available parameters.


Elevation Notch Analysis using Antenna Pattern Data
===================================================

Elevation pointing calibration estimates and corrects any bias between the nominal and actual antenna elevation pointing,
which is critical for accurate SAR data calibration. An incorrect pointing leads to improper compensation of the
**Elevation Antenna Pattern (EAP)**, causing radiometric artifacts such as gain trends in the SAR imagery.

The actual antenna pointing is estimated directly from SAR data, but Antenna Pattern data can be used to properly estimate
the mis-pointing angle using a parametrized model optimized using Least Squares.

Antenna Pattern data is provided as a NetCDF file containing the gain for the swath and polarizations corresponding
to those of the SAR product to be analyzed.

The NetCDF file structure must be as follows:

.. code-block:: text

    <root>
    └── swath
        └── direction (e.g. `TW`)
            └──polarization (e.g. `HH`, `VV`)
                ├── gain (in dB)
                ├── phase (optional, in rad)
                ├── azimuth_angles (in deg)
                └── elevation_angles (in deg)

where ``swath`` is the swath name and ``polarization`` is the actual polarization value. There may be more than one
polarization and/or swath.
