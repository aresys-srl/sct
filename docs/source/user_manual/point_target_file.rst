.. _sct_pt_file:

Calibration Target Data Input File
==================================

In order to perform a Point Target Data analysis using this tool, both from the CLI interface or by using the exposed python
function interfaces, an external Point Target Data file containing calibration target locations and other useful information
must be provided.

To properly orchestrate the whole analysis, a fixed file structure with predefined column names has been choose as a standard
for this application. The template of this .csv file can be downloaded from the GitHub sct/resources folder and filled
by the user with the information needed.

Here is a description of the columns of this file and an example of point target input file.

- ``target_name``: name of the target, i.e. "CR_1" (do not use spaces)
- ``target_type``: type of target, it can be a corner reflector "CR" or an active transponder "TX"
- ``plate``: tectonic plate of reference, information used to compute tectonic displacement if needed
- ``description``: string description of the target, if needed
- ``latitude_deg``: point target location, latitude coordinate in degrees
- ``longitude_deg``: point target location, longitude coordinate in degrees
- ``altitude_m``: point target location, height in meters
- ``x_coord_m``, ``y_coord_m``, ``z_coord_m``: point target location, XYZ coordinates in meters (ECEF system)
- ``drift_velocity_x_my``, ``drift_velocity_y_my``, ``drift_velocity_z_my``: point target measured drift velocities components in meters per year
  these data are used to compute the calibration target displacement with a more accurate estimate
- ``corner_azimuth_deg``, ``corner_elevation_deg``: corner reflector orientation parameters needed for proper RCS computation
- ``target_shape``, ``target_size_m``: corner reflector shape and size needed for proper RCS computation
- ``rcs_hh_dB``, ``rcs_hv_dB``, ``rcs_vv_dB``, ``rcs_vh_dB``: corner reflector RCS magnitude in dB, used to computed RCS error
- ``delay_s``: active calibration target response delay in seconds
- ``measurement_date``: date of measurement of the input data, as an UTC string
- ``validity_start_date``: start date of validity for the given data
- ``validity_stop_date``: end date of validity for the given data


Data validation, enums and conventions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Calibration target data are validated inside the program and several of these columns are needed to perform specific actions
and computations that are optional and can be enable/disabled from the configuration file.

In particular, the following information is mandatory because it corresponds to the bare minimum required to perform the
analysis:

``target_name``, ``target_type``, ``latitude_deg``, ``longitude_deg``, ``altitude_m``, ``x_coord_m``, ``y_coord_m``, ``z_coord_m``

Additional information such as ``plate`` and ``drift_velocity_x_my``, ``drift_velocity_y_my``, ``drift_velocity_z_my`` can
be specified to compute the plate tectonics corrections using the internally defined drift model (just the ``plate`` column
is needed in this case) or by using the user defined drift velocities fro a more accurate estimate.

.. important::

   The ``plate`` value maps to an internal *enum class* providing a list to the available plates supported by the default
   plate tectonics drift model implemented following the **ITRF2014-PMM**. Plate names are those defined `in this paper
   <https://doi.org/10.1093/gji/ggx136>`_.

In these cases, if the plate drift is to be evaluated, ``measurement_date``, ``validity_start_date`` and ``validity_stop_date``
must be populated with UTC dates in order to compute the time interval between the registering of the coordinates provided and
the actual sensor acquisition date.


Dataset Example
^^^^^^^^^^^^^^^

+-------------+-------------+--------+---------------+---------------+----------------+--------------+---------------+---------------+---------------+---------------------+---------------------+---------------------+---------------------+----------------------+---------------+-----------------+-----------+-----------+-----------+-----------+----------+--------------------------+--------------------------+--------------------------+
| target_name | target_type | plate  | description   | latitude_deg  | longitude_deg  |  altitude_m  |   x_coord_m   |   y_coord_m   |  z_coord_m    | drift_velocity_x_my | drift_velocity_y_my | drift_velocity_z_my | corner_azimuth_deg  | corner_elevation_deg |  target_shape |  target_size_m  | rcs_hh_dB | rcs_hv_dB | rcs_vv_dB | rcs_vh_dB | delay_s  | measurement_date         | validity_start_date      |  validity_stop_date      |
+=============+=============+========+===============+===============+================+==============+===============+===============+===============+=====================+=====================+=====================+=====================+======================+===============+=================+===========+===========+===========+===========+==========+==========================+==========================+==========================+
|    CR_1     |      CR     |  AUST  |  Surat Basin  | -26.8347098   |  151.1656039   |   409.4544   | -4989394.0436 | 2746844.3890  | -2862070.0899 | -0.0325             | -0.0083             | 0.0487              |  257.10             |  53.32               |  trihedral    | 1.5             | 0         | 0         | 0         | 0         | 0        | 2020-01-01 00:00:00.000  | 2020-01-01 00:00:00.000  | 2099-01-01 00:00:00.000  |
+-------------+-------------+--------+---------------+---------------+----------------+--------------+---------------+---------------+---------------+---------------------+---------------------+---------------------+---------------------+----------------------+---------------+-----------------+-----------+-----------+-----------+-----------+----------+--------------------------+--------------------------+--------------------------+
|    CR_2     |      CR     |  AUST  |  Surat Basin  | -26.9516331   |  151.2376126   |   432.7094   | -4987723.0920 | 2737761.6619  | -2873635.5867 | -0.0325             | -0.0082             | 0.0486              |  256.21             |  53.33               |  trihedral    | 1.5             | 0         | 0         | 0         | 0         | 0        | 2020-01-01 00:00:00.000  | 2020-01-01 00:00:00.000  | 2099-01-01 00:00:00.000  |
+-------------+-------------+--------+---------------+---------------+----------------+--------------+---------------+---------------+---------------+---------------------+---------------------+---------------------+---------------------+----------------------+---------------+-----------------+-----------+-----------+-----------+-----------+----------+--------------------------+--------------------------+--------------------------+
|    CR_3     |      CR     |  AUST  |  Surat Basin  | -27.1007318   |  151.2588089   |   391.8599   | -4982121.1136 | 2732288.8068  | -2888334.6208 | -0.0326             | -0.0081             | 0.0485              |  258.46             |  54.34               |  trihedral    | 1.5             | 0         | 0         | 0         | 0         | 0        | 2020-01-01 00:00:00.000  | 2020-01-01 00:00:00.000  | 2099-01-01 00:00:00.000  |
+-------------+-------------+--------+---------------+---------------+----------------+--------------+---------------+---------------+---------------+---------------------+---------------------+---------------------+---------------------+----------------------+---------------+-----------------+-----------+-----------+-----------+-----------+----------+--------------------------+--------------------------+--------------------------+
|    CR_4     |      CR     |  AUST  |  Surat Basin  | -27.3088713   |  151.2719591   |   385.2420   | -4973496.3076 | 2726074.1767  | -2908844.8033 | -0.0326             | -0.0079             | 0.0484              |  258.51             |  54.67               |  trihedral    | 1.5             | 0         | 0         | 0         | 0         | 0        | 2020-01-01 00:00:00.000  | 2020-01-01 00:00:00.000  | 2099-01-01 00:00:00.000  |
+-------------+-------------+--------+---------------+---------------+----------------+--------------+---------------+---------------+---------------+---------------------+---------------------+---------------------+---------------------+----------------------+---------------+-----------------+-----------+-----------+-----------+-----------+----------+--------------------------+--------------------------+--------------------------+