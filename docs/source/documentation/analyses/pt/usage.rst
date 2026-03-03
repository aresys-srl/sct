.. _sct_pta_usage: 

Running a Point Target Analysis
===============================

Here is a detailed description on how to execute a Point Target Analysis with SCT in three ways:

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

Point target analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

.. code-block:: bash

    sct [--config <path_to_config>] point_target \
        -p <product_path> -out <output_dir> -pt <point_target_file_path> \
        [-eo <path>] [-ec <path>] [-g]

where ``-g`` is used to enable graphs generation (if added to the command), ``-eo`` is used to specify the path to the
external orbit file, ``-ec`` is used to specify the path to the external corrections product (i.e. ETAD products for Sentinel-1).

.. important::

    | The external source of point targets data provided as a .csv file must be compliant with the template that can be
    | downloaded from the resources folder on GitHub.
    | :ref:`Check the related documentation for further information<sct_pt_file>`.

------------------------------------------------------------
2. Running an Analysis from the Python API
------------------------------------------------------------

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

.. code-block:: python

    from pathlib import Path
    from sct.analyses.point_target.main import full_point_target_analysis
    from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig

    config = SCTPointTargetAnalysisConfig()  # this is the default, but parameters can be set here

    csv_results_path = full_point_target_analysis(
        product=Path("path/to/product"),
        point_target_source=Path("path/to/point_target_source.csv"),
        output_directory=Path("path/to/output_directory"),
        external_orbit=Path("path/to/external_orbit_file"),  # optional, can be None
        external_corrections_product=Path("path/to/external_corrections_product"),  # optional, can be None
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )


------------------------------------------------------------
3. Running an Analysis from the Testing Interface
------------------------------------------------------------

This analysis also provides a testing interface, which can be used to run the analysis from the SCT Testing Framework. To
do so, a registry .json file containing test cases must be created and provided to the testing CLI interface.

.. code-block:: json

    {
        "product-format-type": {
            "test-case-1": {
                "analysis": "point_target",
                "product": "path/to/product/1",
                "config": "path/to/config/if/needed",
                "targets": "path/to/point_target_source.csv",
                "reference_output": "path/to/output/reference/results/csv/for/validation/purposes"
            },
            "test-case-2": {
                "analysis": "point_target",
                "product": "path/to/product/2",
                "config": "path/to/config/if/needed",
                "targets": "path/to/point_target_source.csv",
                "reference_output": "path/to/output/reference/results/csv/for/validation/purposes"
            }
        }
    }

Then the testing CLI interface can be used as follows:

.. code-block:: bash

    sct testing test -r <path_to_registry_file> -out <output_dir> [-g]

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
