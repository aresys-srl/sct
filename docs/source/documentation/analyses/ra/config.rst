.. _sct_ra_config:

Analysis Configuration
----------------------

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

.. note::

    These parameters must be specified in the configuration .toml file under the ``radiometric_analysis`` section.

.. hint::

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

Main Parameters
~~~~~~~~~~~~~~~

.. code-block:: toml
    :linenos:

    [radiometric_analysis]
    input_type = "beta_nought"              # input radiometric quantity
    azimuth_block_size = 2000               # scene partitioning block size in pixel along azimuth
    range_pixel_margin = 150                # margin in pixel to exclude near and far range from profile

.. admonition:: Validation

    | `input_type` maps to an internal *enum class* and is validated by the schema to match the valid values.
    | Here are the possible values:
    | `input_type`: ``beta_nought``, ``sigma_nought``, ``gamma_nought``

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.


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
