.. _sct_config:

Configuration file setup for CLI tool
=====================================

The SCT Command Line Interface (CLI) tool let the user perform quality analyses on input products using the SCT Python
package as a command line executable software. All the implemented features have a dedicated command that can be specified
to perform the operation of choice.
This commands have been developed to be run with a minimal setup and only the essential parameters to be specified, such
as input and output folders.
For an in-depth documentation of how to use the command line tool, please refer :ref:`to this page <sct_cli>`.

Nevertheless, a configuration file (TOML format) can be provided as input to tweak and tune several options and parameters
in order to fully customize each analysis.

This configuration file is designed to work with optional fields that can be specified only if that specific feature should
be altered with respect to the default behavior. In principle, if all default settings are enough for the user, this
configuration file is not necessary.

.. admonition:: Validation

  Configuration files are validated through a JSON schema when provided as input for the tool to assess compliance.


Configuration file structure
----------------------------

The .toml configuration file is organized in sections and subsections related to specific analyses.
*Every section is optional*, except for some fields that are required if certain parameters has been specified.

The available sections of this configuration file are:

- **general**: the highest level of configuration, not related to a specific feature.
- **point_target_analysis**: section that can be used to access *Point Target Analysis* options and parameters.

  * **corrections**: sub-section that can be used to enable/disable some corrections needed for this analysis.
    Refer :ref:`to this page <sct_pta_corrections>` for an in-depth documentation of corrections.

    - **ionosphere**: sub-sub-section dedicated to ionosphere correction customization.
    - **troposphere**: sub-sub-section dedicated to troposphere correction customization.

  * **advanced_configuration**: sub-section that can be used to tweak and tune lower level parameters that can heavily
    alter the behavior of the analysis, if not result in an error.

    - **irf_parameters**: sub-sub-section dedicated to IRF analysis parameters.
    - **rcs_parameters**: sub-sub-section dedicated to RCS analysis parameters.

- **radiometric_analysis**: section that can be used to access *Radiometric Analysis* options and parameters.

  * **advanced_configuration**: sub-section that can be used to tweak and tune lower level parameters that change the
    computation of the radiometric profiles.

    - **parameters**: sub-sub-section dedicated to radiometric profiles parameters.

.. seealso::

   To better understand the implications of changing specific parameters, refer to the :ref:`documentation of the implemented
   analyses <sct_analyses>`.


Detailed description of each section
------------------------------------

A detailed description of each section, sub-section and keywords is herein reported to help the user in setting up a proper
configuration file.

.. important::

   Highlighted lines in the text blocks below means that there is a dependency relationship between those keywords.
   This means that if a specific keyword is a boolean and is set to ``True``, **the other keyword is required**.

.. hint::

   For each TOML text block defined below, the values associated to the keywords are *the defaults*.
   This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
   change that value.


Generic
^^^^^^^

TBD

Point Target Analysis
^^^^^^^^^^^^^^^^^^^^^

The following parameters can be configured directly under the `point_target_analysis` section.

.. code-block:: toml
    :linenos:

    [point_target_analysis]
    perform_irf = true              # on/off IRF computation
    perform_rcs = true              # on/off RCS computation
    evaluate_pslr = true            # on/off PSLR computation
    evaluate_islr = true            # on/off ISLR computation
    evaluate_sslr = true            # on/off SSLR computation
    evaluate_localization = true    # on/off Localization Errors computation
    ale_validity_limits = [x, y]    # set Absolute Localization Error validity limits

.. note::

   `ale_validity_limits` actual default value is ``None`` inside the SCT code. It can be specified as an array of two
   ``float`` values representing the ALE limits in meters along range and azimuth directions.

Corrections
~~~~~~~~~~~

The following parameters can be configured directly under the `point_target_analysis.corrections` section.
`point_target_analysis` **is not required to be defined in the configuration file** for this sub-section to work.

.. code-block:: toml
    :linenos:
    :emphasize-lines: 2,8

    [point_target_analysis.corrections]
    enable_etad_corrections = true                       # on/off ETAD corr.
    enable_solid_tides_correction = true                 # on/off Solid Earth Tides corr.
    enable_plate_tectonics_correction = true             # on/off Plate Tectonics corr.
    enable_sensor_specific_processing_corrections = true # on/off Sensor specific corr.
    enable_ionospheric_correction = false                # on/off Ionospheric corr.
    enable_tropospheric_correction = false               # on/off Tropospheric corr.
    etad_product_path = ""                               # path to the ETAD product

Ionosphere
**********

This sub-sub-section is used when the `point_target_analysis.corrections` ``enable_ionospheric_correction`` flag
is enabled. Just the highlighted rows in the code below **are required** for the code to work.

.. code-block:: toml
    :linenos:
    :emphasize-lines: 2,4,5

    [point_target_analysis.corrections]
    enable_ionospheric_correction = true           # on/off Ionospheric corr.
    [point_target_analysis.corrections.ionosphere]
    ionospheric_maps_directory = ""                # path to the tec map directory
    ionospheric_analysis_center = "cor"            # analysis center (maps provider)

.. admonition:: Validation

   | `ionospheric_analysis_center` and `ionospheric_tec_inc_angle_method` map to internal *enum classes* and are validated by the schema to match these valid values.
   | Here are the possible values:
   | `ionospheric_analysis_center`: ``cor``, ``cod``, ``esa``, ``esr``
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.

Troposphere
***********

This sub-sub-section is used when the `point_target_analysis.corrections` ``enable_tropospheric_correction`` flag
is enabled. Just the highlighted rows in the code below **are required** for the code to work.

.. code-block:: toml
    :linenos:
    :emphasize-lines: 2,4

    [point_target_analysis.corrections]
    enable_tropospheric_correction = true           # on/off Tropospheric corr.
    [point_target_analysis.corrections.troposphere]
    tropospheric_maps_directory = ""                # path to the maps directory
    tropospheric_map_grid_resolution = "fine"       # maps grid resolution

.. admonition:: Validation

   | `tropospheric_map_grid_resolution` maps to an internal *enum class* and is validated by the schema to match the valid values.
   | Here are the possible values:
   | `tropospheric_map_grid_resolution`: ``fine``, ``coarse``
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.


Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

This sub-section cannot be expressed by itself but only through its sub-sections `irf_parameters` and `rcs_parameters`.
This choice has been done to explicitly separate these two configuration categories from the other because changing these
parameters heavily affects the results and can also lead to code errors.

IRF Parameters
**************

This sub-sub-section is used when the the user wants to access low level parameters affecting the IRF computation algorithm.
*This operation is not recommended.*

.. code-block:: toml
    :linenos:

    [point_target_analysis.advanced_configuration.irf_parameters]
    peak_finding_roi_size = [33, 33]            # roi in pixel where to find the signal peak
    analysis_roi_size = [128, 128]              # roi in pixel for processing oversampled image
    oversampling_factor = 16                    # processing oversampling factor
    zero_doppler_abs_squint_threshold_deg = 1.0 # squint angle threshold below which not considering this effect
    masking_method = "peak"                     # masking method for computing IRF quantities

.. admonition:: Validation

   | `masking_method` maps to an internal *enum class* and is validated by the schema to match the valid values.
   | Here are the possible values:
   | `masking_method`: ``peak``, ``resolution``
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.

RCS Parameters
**************

This sub-sub-section is used when the the user wants to access low level parameters affecting the RCS computation algorithm.
*This operation is not recommended.*

.. code-block:: toml
    :linenos:

    [point_target_analysis.advanced_configuration.rcs_parameters]
    interpolation_factor = 8           # processing interpolation factor 
    roi_dimension = 128                # roi (squared) in pixel for processing image
    calibration_factor = 1.0           # rcs calibration factor
    resampling_factor = 1.0            # rcs resampling factor

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.

Radiometric Analysis
^^^^^^^^^^^^^^^^^^^^

The following parameters can be configured directly under the `radiometric_analysis` section.

.. code-block:: toml
    :linenos:

    [radiometric_analysis]
    input_type = "beta_nought"         # input radiometric quantity
    output_type = "beta_nought"        # output radiometric quantity
    value = "amplitude"                # radiometric analysis value to be outputted
    direction = "range"                # direction along which perform analysis
    axis = "natural"                   # axis on which display output values
    outlier_removal = false            # on/off outliers removal filter
    smoothening_filter = true          # on/off smoothening filter

.. admonition:: Validation

   | `input_type`, `output_type`, `value`, `direction`, `axis` map to an internal *enum classes* and are validated by the schema to match the valid values.
   | Here are the possible values:
   | `input_type` / `output_type`: ``beta_nought``, ``sigma_nought``, ``gamma_nought``
   | `value`: ``amplitude``, ``phase``
   | `direction`: ``range``, ``azimuth``, ``all``
   | `axis`: ``natural``, ``incidence_angle``, ``look_angle``
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.


Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

This sub-section cannot be expressed by itself but only through its sub-section `parameters`.
`radiometric_analysis` **is not required to be defined in the configuration file** for this sub-section to work.
Changing these parameters can heavily affect the analysis.

.. code-block:: toml
    :linenos:

    [radiometric_analysis.advanced_configuration.parameters]
    smoothening_order = 3                       # smoothening poly order
    smoothening_window_length = 71              # smoothening window length
    radiometric_correction_exponent = 0.5       # radiometric correction exponent
    outliers_kernel_size = [5, 5]               # outliers removal kernel size
    outliers_filter_kernel_size = [10, 10]      # outliers filtering kernel size
    outliers_percentile_boundaries = [20, 90]   # inliers percentiles limits
    az_average_band = 1000                      # azimuth averaging band in pixels
    rng_average_band = 1000                     # range averaging band in pixels

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.
