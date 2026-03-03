.. _sct_ptar_usage: 

Running a Point Target Ambiguity Ratio Analysis
===============================================

Here is a detailed description on how to execute a Point Target Analysis with SCT in two ways:

1. From the **Command Line Interface (CLI)**  → user-facing execution
2. From the **Python API**  → programmatic/scripting/orchestration integration

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

PTAR analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

.. code-block:: bash

    sct [--config <path_to_config>] ambiguity_ratio -p <product_path> -out <output_dir> -pt <point_target_file_path>

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
    from sct.analyses.ambiguity_ratio.main import full_pt_ambiguity_ratio_analysis
    from sct.analyses.ambiguity_ratio.config import SCTTargetAmbiguityRatioConfig

    config = SCTTargetAmbiguityRatioConfig()  # this is the default, but parameters can be set here

    full_pt_ambiguity_ratio_analysis(
        product=Path("path/to/product"),
        point_target_source=Path("path/to/point_target_source.csv"),
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )
