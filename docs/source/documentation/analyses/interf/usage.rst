Running an Interferometric Analysis
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

Interferometric analysis can be performed using the following command just specifying the input product and the output directory.


.. code-block:: bash

    sct [--config <path_to_config>] interferometry -p <product_path> -out <output_dir> [-g]

where ``-g`` is used to enable graphs generation (if added to the command). The input product must be an interferogram product
or a coherence map product.

If the user wants to compute the coherence map from two co-registered products, the user must use the following
command:

.. code-block:: bash

    sct [--config <path_to_config>] interferometry -p <product_path_1> -pp <product_path_2> -out <output_dir> [-g]

where ``-p`` and ``-pp`` are the paths to the two co-registered products.

------------------------------------------------------------
2. Running an Analysis from the Python API
------------------------------------------------------------

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

.. code-block:: python

    from pathlib import Path
    from sct.analyses.interferometry.main import full_interferometric_analysis
    from sct.analyses.interferometry.config import SCTInterferometricAnalysisConfig

    config = SCTInterferometricAnalysisConfig()  # this is the default, but parameters can be set here

    output_netcdf_file = full_interferometric_analysis(
        product=Path("path/to/product"),
        product_2=Path("path/to/product_2"),  # optional, can be None
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
            "test-case-1": {
                "analysis": "interferometry",
                "product": [
                    "path/to/co-registered-product/1",
                    "path/to/co-registered-product/2"
                ],
                "config": "path/to/config/if/needed",
                "reference_output": "path/to/output/reference/results/coherence_histograms.nc"
            },
            "test-case-2": {
                "analysis": "interferometry",
                "product": "path/to/interferogram-product",
                "config": "path/to/config/if/needed",
                "reference_output": "path/to/output/reference/results/coherence_histograms.nc"
            },
        }
    }

Then the testing CLI interface can be used as follows:

.. code-block:: bash

    sct testing test -r <path_to_registry_file> -out <output_dir> [-g]

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
