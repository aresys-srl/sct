.. _sct_spectra_config:

Analysis Configuration
----------------------

This analysis can be configured and algorithms customized through the configuration file. Here is a brief description
of the available parameters that can be set.

.. note::

    These parameters must be specified in the configuration .toml file under the ``spectral_analysis`` section.

.. hint::

    For each TOML text block defined below, the values associated to the keywords are *the defaults*.
    This means that **there is no need to specify those values** in the configuration file unless the intention is to explicitly
    change that value.

Main Parameters
~~~~~~~~~~~~~~~

.. code-block:: toml
    :linenos:

    [spectral_analysis]
    cropping_size = [128, 128]                 # ROI size to be analyzed

:ref:`Check the API documentation<sct_api_ref_index>` to learn more about these values and their meaning.
