.. _sct_tutorials:

Quick Start and Tutorials
=========================

This is a collection of simple examples on how to perform specific tasks using the SCT software, both from the CLI interface
and as a python library.

Point Target Analysis
---------------------

To perform a Point Target Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

.. code-block:: bash

    sct --config path_to_config_toml target-analysis -p path_to_product -out path_to_output_folder -pt path_to_target_csv_file [-eo path_to_external_orbit] [-g]

If an external orbit must be used for a Sentinel-1 product, it can be passed as input to the CLI tool using the `--external-orbit/-eo` option.
Graphical output for point target analysis can be enabled using the `--graphs/-g` option for the CLI tool.

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from sct.configuration.sct_configuration import SCTConfiguration
    from sct.analyses.point_target_analysis import point_target_analysis_with_corrections
    from sct.analyses.graphical_output import sct_pta_graphs  # optional, for graphs only

    # adding a configuration is optional
    config_toml_path = ...
    config = SCTConfiguration.from_toml(config_toml_path)
    # adding an external orbit for Sentinel 1 products is optional
    path_to_external_orbit = ...
    product_path = ...
    targets_csv_file_path = ...
    output_results_csv_file = ...
    graphs_output_directory = ...

    results_df, data_for_graphs = pta.point_target_analysis_with_corrections(
        product_path=prod,
        external_target_source=targets_csv_file_path,
        external_orbit_path=path_to_external_orbit,  # optional
        config=config.point_target_analysis,  # optional
    )
    results_df.to_csv(output_results_csv_file, index=False)

    # optional, if graphical output is needed
    sct_pta_graphs(graphs_data=data_for_graphs, results_df=results_df, output_dir=graphs_output_directory)

.. seealso::

   Any other feature can be enabled using the configuration .toml input file. Please, refer to the :ref:`documentation about tool configuration <sct_config>`.


Using external Ionospheric and Tropospheric Maps to compute perturbations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Input configuration file must contain the following lines to be able to perform a Point Target Analysis taking into account
atmospheric perturbations from external maps.

.. code-block:: toml

    # both or just one of the two perturbations can be selected
    [point_target_analysis.corrections]
    enable_ionospheric_correction = true
    enable_tropospheric_correction = true

    [point_target_analysis.corrections.ionosphere]
    ionospheric_maps_directory = "path/to/ionospheric/maps/directory"
    ionospheric_analysis_center = "cor"

    [point_target_analysis.corrections.troposphere]
    tropospheric_maps_directory = "path/to/tropospheric/maps/directory"
    tropospheric_map_grid_resolution = "fine"

Using ETAD products for Sentinel-1 data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Input configuration file must contain the following lines to be able to perform a Point Target Analysis taking into account
an external ETAD products to compute perturbations.

.. code-block:: toml

    [point_target_analysis.corrections]
    enable_etad_corrections = true
    etad_product_path = "path/to/etad/product"

Radiometric Analysis
--------------------

To perform a Radiometric Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

.. note::

    Input radiometric quantity of the product is set to be **BETA_NOUGHT** by default. This property can be changed via
    configuration by adding ``[radiometric_analysis] input_quantity = "sigma_nought"`` inserting the proper radiometric quantity.

.. code-block:: bash

    sct --config path_to_config_toml radiometric-analysis [nesz/elevation_profile/scalloping] -p path_to_product -out path_to_output_folder [-g] [-r "output_radiometric_quantity"]

Graphical output for radiometric analysis can be enabled using the `--graphs/-g` option for the CLI tool.

Average radiometric profiles output radiometric quantity can be setup by using the `--output_radiometric_quantity/-r` option.

.. admonition:: Validation

   | `output_radiometric_quantity` maps to an internal *enum class*.
   | Here are the possible values:
   | `input_type`: ``beta``, ``sigma``, ``gamma``

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from pathlib import Path
    from sct.configuration.sct_configuration import SCTConfiguration
    import sct.analyses.radiometric_analysis as ra
    from arepyextras.quality.radiometric_analysis.support import radiometric_profiles_to_netcdf  # optional, if netCDF saving is needed
    from arepyextras.quality.radiometric_analysis.graphical_output import radiometric_2D_hist_plot  # optional, if graphs are needed
    from arepyextras.quality.core.generic_dataclasses import SARRadiometricQuantity

    # adding a configuration is optional
    config_toml_path: str | Path = ...
    config = SCTConfiguration.from_toml(config_toml_path)
    # specify the input radiometric quantity if different from BETA NOUGHT
    config.radiometric_analysis.base_config.input_quantity = SARRadiometricQuantity.SIGMA_NOUGHT
    product_path: str | Path = ...
    output_directory: str | Path = ...
    output_radiometric_quantity = SARRadiometricQuantity.GAMMA_NOUGHT

    tag = "nesz"
    results = ra.nesz_analysis(product_path=product, config=config.radiometric_analysis)
    # or
    tag = "average_gamma"
    results = ra.average_elevation_profile_analysis(
        product_path=product,
        output_quantity=output_radiometric_quantity,
        config=config.radiometric_analysis
    )
    # or
    tag = "scalloping"
    results = ra.scalloping_analysis(product_path=product, config=config.radiometric_analysis)

    for item in results:
        radiometric_profiles_to_netcdf(data=item, out_path=output_directory, tag=tag)

        # optional, if graphical output is needed
        radiometric_2D_hist_plot(
            data=item,
            out_dir=output_directory,
            title=f"{tag.upper()} Profiles {item.swath} {item.polarization.name}",
        )

Interferometric Analysis
------------------------

To perform an Interferometric Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

.. note::

    Coherence computation is disabled by default for a single product input (while it's enabled when two products are provided).
    To enable its computation, provide a config with ``[interferometric_analysis] enable_coherence_computation = true``.

.. code-block:: bash

    sct --config path_to_config_toml interferometric-analysis -p path_to_product -out path_to_output_folder -pp path_to_second_product [-g]

Graphical output for interferometric analysis can be enabled using the `--graphs/-g` option for the CLI tool.

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from pathlib import Path
    from arepyextras.quality.interferometric_analysis.graphical_output import generate_coherence_graphs
    from arepyextras.quality.interferometric_analysis.support import coherence_histograms_to_netcdf

    from sct.analyses import interferometric_analysis as interf
    from sct.configuration.sct_configuration import SCTInterferometricAnalysisConfig

    product_path: str | Path = ...
    output_dir: str | Path = ...
    config = SCTInterferometricAnalysisConfig()
    config.base_config.enable_coherence_computation = True

    output = interf.interferometric_coherence_analysis(product_path=prod, config=config)
    for out in output:
        generate_coherence_graphs(out, output_dir=out_dir, mode="magnitude")
        generate_coherence_graphs(out, output_dir=out_dir, mode="phase")
        coherence_histograms_to_netcdf(out, output_dir=out_dir)
