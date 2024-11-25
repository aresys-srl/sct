.. _sct_config:

Configuration file setup for CLI tool
=====================================

The SCT Command Line Interface (CLI) tool let the user perform quality analyses on input products using the SCT Python
package as a command line executable software. All the implemented features have a dedicated command that can be specified
to perform the operation of choice.
This commands have been developed to be run with a minimal setup and only the essential parameters to be specified, such
as input and output folders.
For an in-depth documentation on how to use the command line tool, please refer :ref:`to this page <sct_cli>`.

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

    - **profile_extraction_parameters**: sub-sub-section dedicated to radiometric profiles parameters.
    - **histogram_parameters**: sub-sub-section dedicated to radiometric 2D histograms parameters.

- **interferometric_analysis**: section that can be used to access *Interferometric Analysis* options and parameters.


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

The following parameters can be configured directly under the `general` section.

.. code-block:: toml
    :linenos:

    [general]
    save_log = true                 # save analysis log to output folder
    save_config_copy = true         # save analysis config to output folder


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
    ale_validity_limits = [99, 99]  # set Absolute Localization Error validity limits in meters [rng, az]

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
This choice has been done to explicitly separate these two configuration categories from the others because changing these
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
    input_type = "beta_nought"              # input radiometric quantity
    azimuth_block_size = 2000               # scene partitioning block size in pixel along azimuth
    range_pixel_margin = 150                # margin in pixel to exclude near and far range from profile
    radiometric_correction_exponent = 1.0   # radiometric correction exponent applied when converting radiometric quantity

.. admonition:: Validation

   | `input_type` maps to an internal *enum class* and is validated by the schema to match the valid values.
   | Here are the possible values:
   | `input_type`: ``beta_nought``, ``sigma_nought``, ``gamma_nought``
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.


Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

This sub-section cannot be expressed by itself but only through its sub-sections `profile_extraction_parameters` and `histogram_parameters`.
This choice has been done to explicitly separate these two configuration categories from the others because changing these
parameters heavily affects the results.
`radiometric_analysis` **is not required to be defined in the configuration file** for this sub-section to work.
Changing these parameters can heavily affect the analysis.

Profile Extraction Parameters
*****************************

This sub-sub-section is used when the the user wants to access low level parameters affecting the radiometric profiles
extraction algorithm.

.. code-block:: toml
    :linenos:

    [radiometric_analysis.advanced_configuration.profile_extraction_parameters]
    outlier_removal = false                     # enabling/disabling outlier removal filter
    smoothening_filter = false                  # enabling/disabling smoothening filter
    filtering_kernel_size = [11, 11]            # size of the smoothening filter kernel
    outliers_kernel_size = [5, 5]               # size of the outliers removal kernel
    outliers_percentile_boundaries = [20, 90]   # outliers percentile boundaries to be preserved

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.

2D Histograms Parameters
************************

This sub-sub-section is used when the the user wants to access low level parameters affecting the computation algorithm
of the 2D histograms.

.. code-block:: toml
    :linenos:

    [radiometric_analysis.advanced_configuration.histogram_parameters]
    x_bins_step = 10            # number of bins along the x axis [look angles/azimuth times]
    y_bins_num = 101            # number of bins along the y axis [intensity (dB)]
    y_bins_center_margin = 3    # extent of the intensity graph (in dB) from the central bin

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.


Interferometric Analysis
^^^^^^^^^^^^^^^^^^^^^^^^

The following parameters can be configured directly under the `interferometric_analysis` section.

.. code-block:: toml
    :linenos:

    [interferometric_analysis]
    enable_coherence_computation = false        # enable/disable coherence computation (to be enabled for interferogram products)
    coherence_kernel = [15, 15]                 # kernel size for coherence computation
    azimuth_blocks_number = 1                   # number of azimuth blocks for computing coherence 2D histogram
    range_blocks_number = 1                     # number of range blocks for computing coherence 2D histogram
    coherence_bins_number = 80                  # number of coherence intensity bins

.. admonition:: Validation

   | `azimuth_blocks_number` and `range_blocks_number` are actually automatically computed if not explicitly set from configuration.
   | :ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.
