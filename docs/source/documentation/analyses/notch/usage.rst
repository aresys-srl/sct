Running an Elevation Notch Analysis
===================================

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

Elevation Notch analysis can be performed using the following command just specifying the input product and the output directory.

.. code-block:: bash

    sct [--config <path_to_config>] elevation_notch -p <product_path> -out <output_dir> [-ap <antenna_pattern>] [-g]

where ``-g`` is used to enable graphs generation (if added to the command). The antenna pattern file can be provided in
NetCDF format using the ``-ap`` flag.

------------------------------------------------------------
2. Running an Analysis from the Python API
------------------------------------------------------------

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

.. code-block:: python

    from pathlib import Path
    from sct.analyses.elevation_notch.main import full_elevation_notch_analysis
    from sct.analyses.elevation_notch.config import SCTElevationNotchAnalysisConfig

    config = SCTElevationNotchAnalysisConfig()  # this is the default, but parameters can be set here

    output_netcdf_file = full_elevation_notch_analysis(
        product=Path("path/to/product"),
        antenna_pattern=Path("path/to/antenna_pattern.nc"),  # optional, can be None
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )

------------------------------------------------------------
3. Running an Analysis from the Testing Interface
------------------------------------------------------------

The interferometric analysis implementation also provides a testing interface, which can be used to run the analysis from the
SCT Testing Framework. To do so, a registry .json file containing test cases must be created and provided to the testing
CLI interface.


.. code-block:: json

    {
        "product-format-type": {
            "notch": {
                "analysis": "elevation_notch",
                "product": "path/to/product",
                "config": "path/to/config/if/needed",
                "antenna_pattern": "path/to/antenna_pattern.nc",
                "reference_output": "path/to/output/reference/results/elevation_notch_results.nc"
            }
        }
    }

Then the testing CLI interface can be used as follows:

.. code-block:: bash

    sct testing test -r <path_to_registry_file> -out <output_dir> [-g]

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
