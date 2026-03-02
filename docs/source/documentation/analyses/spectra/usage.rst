Running a Spectral Analysis
===========================

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

Point Target
~~~~~~~~~~~~

Spectral analysis on point targets can be performed using the following command just specifying the input product, the point
target locations file and the output directory.

.. code-block:: bash

    sct [--config <path_to_config>] spectral-analysis -p <product_path> -pt <point_target_file_path> -out <output_dir> [-g]

where ``-g`` is used to enable graphs generation (if added to the command). 

.. important::

    | The external source of point targets data provided as a .csv file must be compliant with the template that can be
    | downloaded from the resources folder on GitHub.
    | :ref:`Check the related documentation for further information<sct_pt_file>`.

Distributed
~~~~~~~~~~~

If the user wants to compute the Spectral Analysis on distributed products, the user must use the following command:

.. code-block:: bash

    sct [--config <path_to_config>] spectral-analysis -p <product_path> -out <output_dir> [-g]

------------------------------------------------------------
2. Running an Analysis from the Python API
------------------------------------------------------------

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

.. code-block:: python

    from pathlib import Path
    from sct.analyses.spectra.main import full_spectral_analysis
    from sct.analyses.spectra.config import SCTSpectralAnalysisConfig

    config = SCTSpectralAnalysisConfig()  # this is the default, but parameters can be set here

    output_netcdf_file = full_spectral_analysis(
        product=Path("path/to/product"),
        point_target_source=Path("path/to/point_target_source.csv"),  # optional, can be None for distributed analysis
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
                "analysis": "spectra",
                "product": "path/to/product",
                "config": "path/to/config/if/needed",
                "targets": "path/to/point_target_source.csv",
                "reference_output": "path/to/output/reference/results/spectral_profiles.nc"
            }
        }
    }

Then the testing CLI interface can be used as follows:

.. code-block:: bash

    sct-testing -r <path_to_registry_file> -out <output_dir> [-g]

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
