.. _sct_notch_config:

Analysis Configuration
----------------------

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

.. note::

    These parameters must be specified in the configuration .toml file under the ``elevation_notch_analysis`` section.

.. hint::

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

Main Parameters
~~~~~~~~~~~~~~~

.. code-block:: toml
    :linenos:

    [elevation_notch_analysis]
    azimuth_block_size = 2500               # scene partitioning block size in pixel along azimuth
    range_pixel_margin = 100                # margin in pixel to exclude near and far range from profile

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.
