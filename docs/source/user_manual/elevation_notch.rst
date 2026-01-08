.. _sct_notch_antenna:

Elevation Notch Analysis using Antenna Pattern Data
===================================================

Elevation pointing calibration estimates and corrects any bias between the nominal and actual antenna elevation pointing,
which is critical for accurate SAR data calibration. An incorrect pointing leads to improper compensation of the
Elevation Antenna Pattern (EAP), causing radiometric artifacts such as gain trends in the SAR imagery.

The actual antenna pointing is estimated directly from SAR data, but Antenna Pattern data can be used to properly estimate
the mis-pointing angle using a parametrized model optimized using Least Squares.

Antenna Pattern data is provided as a NetCDF file containing the gain for the swath and polarizations corresponding
to those of the SAR product to be analyzed.

The NetCDF file structure must be as follows:

.. code-block:: text

    <root>
    └── swath
        └── polarization
            ├── gain (in dB)
            ├── phase (optional, in rad)
            ├── azimuth_angles (in deg)
            └── elevation_angles (in deg)

where ``swath`` is the swath name and ``polarization`` is the actual polarization value. There may be more than one
polarization and/or swath.
