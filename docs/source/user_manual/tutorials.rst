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

    sct --config path_to_config_toml target-analysis -p path_to_product -out path_to_output_folder -pt path_to_target_csv_file [-eo path_to_external_orbit] [-ec path_to_external_corrections] [-g]

If an external orbit must be used for a Sentinel-1 product, it can be passed as input to the CLI tool using the `--external-orbit/-eo` option.
Graphical output for point target analysis can be enabled using the `--graphs/-g` option for the CLI tool.

Auxiliary external products containing the corrections to be applied to the SAR Product quality analysis, such as ETAD
products for Sentinel-1, can be provided as input for both the CLI and the API main Point Target Analysis function, using
respectively the `--external-corrections/-ec` option or the ``external_corrections_product`` optional input argument.

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from collections.abc import Callable
    from pathlib import Path
    from sct.configuration.sct_configuration import SCTConfiguration
    from sct.orchestration import full_point_target_analysis_implementation
    from perseo_quality.point_targets_analysis.graphical_output import point_target_graphs_generation

    product_path: str | Path = ...
    point_target_source_file_path: str | Path = ...  # CSV file containing the point target source
    output_dir: str | Path = ...
    config: SCTConfiguration | None = ...
    graphs_func: Callable | None = point_target_graphs_generation

    path_to_external_orbit: str | Path | None = ...  # support for Sentinel 1 products only, optional
    path_to_external_correction_product: str | Path | None = ...  # i.e. ETAD product for Sentinel-1, optional

    output_csv_path = full_point_target_analysis_implementation(
        product=product_path,
        external_orbit=path_to_external_orbit,
        external_corrections_product=path_to_external_correction_product,
        point_target_source=point_target_source_file_path,
        output_directory=output_dir,
        config=config,
        graphs_func=graphs_func,
    )

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


Radiometric Analysis
--------------------

To perform a Radiometric Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

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

    ### NESZ Analysis Example###

    from collections.abc import Callable
    from pathlib import Path
    from sct.configuration.sct_configuration import SCTConfiguration
    from sct.orchestration import full_nesz_implementation
    from perseo_quality.radiometric_analysis.block_wise.graphical_output import radiometric_2D_hist_plot

    product_path: str | Path = ...
    output_dir: str | Path = ...
    config: SCTConfiguration | None = ...
    graphs_func: Callable | None = radiometric_2D_hist_plot

    output_netcdf_path, output_kpi_csv_path = full_nesz_implementation(
        product=product_path,
        output_directory=output_directory,
        config=config,
        graphs_func=graphs_func,
    )

    ### RAIN FOREST Analysis Example###

    from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
    from sct.orchestration import full_average_elevation_profiles_implementation

    output_radiometric_quantity = SARRadiometricQuantity.GAMMA_NOUGHT

    output_netcdf_path, output_kpi_csv_path = full_average_elevation_profiles_implementation(
        product=product_path,
        output_radiometric_quantity=output_radiometric_quantity,
        output_directory=output_dir,
        config=config,
        graphs_func=graphs_func,
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

    from collections.abc import Callable
    from pathlib import Path
    from sct.configuration.sct_configuration import SCTConfiguration
    from sct.orchestration import full_interferometric_analysis_implementation
    from perseo_quality.interferometric_analysis.graphical_output import generate_coherence_graphs

    product_path: str | Path = ...
    second_product_path: str | Path | None = ...
    output_dir: str | Path = ...
    config: SCTConfiguration | None = ...
    graphs_func: Callable | None = generate_coherence_graphs

    output_netcdf_path = full_interferometric_analysis_implementation(
        product=product_path,
        product_2=second_product_path,
        output_directory=output_dir,
        config=config,
        graphs_func=graphs_func,
    )


Elevation Notch Analysis
------------------------

To perform an Elevation Notch Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

.. code-block:: bash

    sct --config path_to_config_toml notch-analysis -p path_to_product -out path_to_output_folder [-ap path_to_second_product] [-g]

.. note::

    Elevation Notch computation can be performed with or without passing an antenna pattern NetCDF to the CLI tool.
    Check the documentation about this analysis for more details.

Graphical output for elevation notch analysis can be enabled using the `--graphs/-g` option for the CLI tool.

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from collections.abc import Callable
    from pathlib import Path
    from sct.orchestration import full_elevation_notch_analysis_implementation
    from perseo_quality.elevation_notch_analysis.graphical_output import plot_elevation_notch_analysis

    product_path: str | Path = ...
    output_directory: str | Path = ...
    config: SCTConfiguration | None = ...
    graphs_func: Callable | None = plot_elevation_notch_analysis

    output_netcdf_path = full_elevation_notch_analysis_implementation(
        product=product_path,
        antenna_pattern=antenna_pattern_path,
        output_directory=output_directory,
        config=config,
        graphs_func=graphs_func,
    )

