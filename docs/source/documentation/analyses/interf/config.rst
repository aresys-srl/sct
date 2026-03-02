.. _sct_interf_config:

Analysis Configuration
----------------------

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

.. note::

    These parameters must be specified in the configuration .toml file under the ``interferometric_analysis`` section.

.. hint::

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

Main Parameters
~~~~~~~~~~~~~~~

.. code-block:: toml
    :linenos:

    [interferometric_analysis]
    enable_coherence_computation = false        # enable/disable coherence computation (to be enabled for interferogram products)
    coherence_kernel = [15, 15]                 # kernel size for coherence computation
    azimuth_blocks_number = 10                  # number of azimuth blocks for computing coherence 2D histogram
    range_blocks_number = 15                    # number of range blocks for computing coherence 2D histogram
    coherence_bins_number = 80                  # number of coherence intensity bins

.. admonition:: Validation

    | `azimuth_blocks_number` and `range_blocks_number` are actually automatically computed if not explicitly set from configuration.

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.
