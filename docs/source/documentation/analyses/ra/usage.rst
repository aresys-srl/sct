.. _sct_ra_usage: 

Running a Radiometric Analysis
==============================

Here is a detailed description on how to execute a Radiometric Analysis with SCT in three ways:

1. From the **Command Line Interface (CLI)**  → user-facing execution
2. From the **Python API**  → programmatic/scripting/orchestration integration
3. From the **SCT Testing Interface**  → automated validation

Prerequisites
-------------

Before running any analysis:

- SCT must be installed
- A valid product must be available and :ref:`its format plugin installed<sct_format_plugins>`
- A configuration file in TOML format (optional)
- A testing registry (optional)

------------------------------------------------------------
1. Running an Analysis from the CLI
------------------------------------------------------------

Several radiometric analyses have been implemented with a dedicated command that can be specified to perform the operation of choice.
They have been grouped under the ``radiometric-analysis`` CLI group.

NESZ
~~~~

NESZ analysis can be performed using the following command just specifying the input product and the output directory.

.. code-block:: bash

    sct [--config <path_to_config>] radiometric-analysis nesz -p <product_path> -out <output_dir> [-g]

where ``-g`` is used to enable graphs generation (if added to the command).

Average Elevation Profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~

Average Elevation Profiles analysis can be performed using the following command just specifying the input product, the
output directory and the desired output radiometric quantity.

.. code-block:: bash

    sct [--config <path_to_config>] radiometric-analysis elevation-profile -p <product_path> -out <output_dir> -r <radiometric_quantity> [-g]

where ``-g`` is used to enable graphs generation (if added to the command) and ``<radiometric_quantity>`` is the desired
output radiometric quantity (``sigma``, ``gamma`` or ``beta``).

Scalloping
~~~~~~~~~~

Scalloping analysis can be performed using the following command just specifying the input product and the output directory.

.. code-block:: bash

    sct [--config <path_to_config>] radiometric-analysis scalloping -p <product_path> -out <output_dir> [-g]

where ``-g`` is used to enable graphs generation (if added to the command).

------------------------------------------------------------
2. Running an Analysis from the Python API
------------------------------------------------------------

These analyses is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

.. code-block:: python

    from pathlib import Path
    from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
    from sct.analyses.radiometry.main import (
        full_nesz_analysis,
        full_average_elevation_profiles_analysis,
        full_scalloping_analysis
    )
    from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig

    config = SCTRadiometricAnalysisConfig()  # this is the default, but parameters can be set here

    output_netcdf_file, output_kpi_file = full_nesz_analysis(
        product=Path("path/to/product"),
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )

    output_netcdf_file, output_kpi_file = full_average_elevation_profiles_analysis(
        product=Path("path/to/product"),
        output_radiometric_quantity=SARRadiometricQuantity.SIGMA,
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )

    output_netcdf_file, output_kpi_file = full_scalloping_analysis(
        product=Path("path/to/product"),
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )


------------------------------------------------------------
3. Running an Analysis from the Testing Interface
------------------------------------------------------------

The radiometric analysis implementation also provides a testing interface, which can be used to run the analysis from the
SCT Testing Framework. To do so, a registry .json file containing test cases must be created and provided to the testing
CLI interface.

.. note::

    Regarding the Average Elevation Profiles analysis, only the ``RAIN_FOREST`` (gamma profiles) analysis is currently
    supported via testing interface.

.. code-block:: json

    {
        "product-format-type": {
            "test-case-1": {
                "analysis": "radiometry-nesz",
                "product": "path/to/product/1",
                "config": "path/to/config/if/needed",
                "reference_output": [
                    "path/to/output/reference/results/kpi_stats.csv",
                    "path/to/output/reference/results/NESZ_profiles.nc"
                ]
            },
            "test-case-2": {
                "analysis": "radiometry-rain-forest",
                "product": "path/to/product/2",
                "config": "path/to/config/if/needed",
                "reference_output": [
                    "path/to/output/reference/results/kpi_stats.csv",
                    "path/to/output/reference/results/RAIN_FOREST_profiles.nc"
                ]
            },
            "test-case-3": {
                "analysis": "radiometry-scalloping",
                "product": "path/to/product/3",
                "config": "path/to/config/if/needed",
                "reference_output": [
                    "path/to/output/reference/results/kpi_stats.csv",
                    "path/to/output/reference/results/SCALLOPING_profiles.nc"
                ]
            }
        }
    }

Then the testing CLI interface can be used as follows:

.. code-block:: bash

    sct-testing -r <path_to_registry_file> -out <output_dir> [-g]

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
