Quick Start & Tutorials
=======================

This section provides a focused collection of practical examples to help you get started with the Radiometric analysis
in SCT. The tutorials demonstrate how to perform common tasks both through the command-line interface (CLI) and by using
SCT as a Python library.

Each example walks through a specific workflow step-by-step, highlighting recommended practices and typical use cases.
By following these guides, you will quickly learn how to configure and run this analysis.

Use this section as your starting point for understanding and applying the Point Target workflow effectively.

Basic usage
-----------

Radiometric Analysis can be performed using CLI or Python API, as described in the :ref:`documentation about Point Target Analysis <sct_ra_usage>`.

Rain Forest Analysis
^^^^^^^^^^^^^^^^^^^^

Rain Forest Analysis can be performed on dedicated SAR Products containing acquisitions recorded over Rain Forest sites by
using the Average Elevation Profiles functionality customizing the output radiometric quantity to be ``gamma``.

.. code-block:: bash

    sct [--config <path_to_config>] radiometric-analysis elevation-profile -p <product_path> -out <output_dir> -r gamma [-g]

To perform a Radiometric Analysis using SCT CLI, run the following command in your shell, adapting the input parameters
to your needs. Passing the input configuration can be avoided if default values are good enough.

The exact same thing can be done from a custom script using SCT as a library:

.. code-block:: python

    from pathlib import Path
    from perseo_quality.core.generic_dataclasses import SARRadiometricQuantity
    from sct.analyses.radiometry.main import full_average_elevation_profiles_analysis
    from sct.analyses.radiometry.config import SCTRadiometricAnalysisConfig

    output_netcdf_file, output_kpi_file = full_average_elevation_profiles_analysis(
        product=Path("path/to/product"),
        output_radiometric_quantity=SARRadiometricQuantity.GAMMA,
        output_directory=Path("path/to/output_directory"),
        config=config,  # optional, can be None
        graphs=True,  # optional, can be False
    )
