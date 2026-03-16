---
icon: lucide/wrench
title: "Usage"
tags:
    - radiometric analysis
    - nesz
    - rain forest
    - radiometric profiles
    - scalloping
    - tutorials
    - CLI
    - python
    - testing
---

# Running an Radiometric Analysis

Here is a detailed description on how to execute a Radiometric Analysis with SCT in three ways:

1. From the [__Command Line Interface (CLI)__](#cli-analysis)  → user-facing execution
2. From the [__Python API__](#api-analysis)  → programmatic/scripting/orchestration integration
3. From the [__Testing Interface__](#testing-analysis)  → automated validation

!!! info "Prerequisites"

    - SCT must be installed
    - A valid product must be available and [its format plugin installed](../../../format_plugins.md)
    - A configuration file in TOML format (optional)
    - A testing registry (optional)

## From CLI {#cli-analysis}

Several radiometric analyses have been implemented with a dedicated command that can be specified to perform the operation of choice.
They have been grouped under the ``radiometry`` CLI group.

### NESZ

NESZ analysis can be performed using the following command just specifying the input product and the output directory.

```bash title="CLI command"
sct [--config <path_to_config>] radiometry nesz -p <product_path> -out <output_dir> [-g]
```

where ``-g`` is used to enable graphs generation (if added to the command).

### Average Elevation Profiles

Average Elevation Profiles analysis can be performed using the following command just specifying the input product, the
output directory and the desired output radiometric quantity.

```bash title="CLI command"
sct [--config <path_to_config>] radiometry elevation-profiles -p <product_path> -out <output_dir> -r <radiometric_quantity> [-g]
```

where ``-g`` is used to enable graphs generation (if added to the command) and ``<radiometric_quantity>`` is the desired
output radiometric quantity (``sigma``, ``gamma`` or ``beta``).

### Rain Forest

Rain Forest analysis can be performed using the following command just specifying the input product and the output directory.
This analysis is just a shortcut for ``radiometry elevation-profiles -r gamma`` where the output radiometric quantity
is automatically set to ``gamma``.

```bash title="CLI command"
sct [--config <path_to_config>] radiometry rain-forest -p <product_path> -out <output_dir> [-g]
```

### Scalloping

Scalloping analysis can be performed using the following command just specifying the input product and the output directory.

```bash title="CLI command"
sct [--config <path_to_config>] radiometry scalloping -p <product_path> -out <output_dir> [-g]
```

where ``-g`` is used to enable graphs generation (if added to the command).

## From Python API {#api-analysis}

These analyses is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

```python linenums="1" title="Python API"
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
    output_radiometric_quantity=SARRadiometricQuantity.SIGMA,  # GAMMA for Rain Forest
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
```

## From Testing Interface {#testing-analysis}

The radiometric analysis implementation also provides a testing interface, which can be used to run the analysis from the
SCT Testing Framework. To do so, a registry .json file containing test cases must be created and provided to the testing
CLI interface.

```json title="testing_registry.json"
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
```

!!! warning "Average Elevation Profiles Testing"

    Regarding the *Average Elevation Profiles* analysis, only the **Rain Forest** (gamma profiles) analysis is currently
    supported via testing interface.

Then the testing CLI interface can be used as follows:

```bash title="Testing Interface"
sct testing test -r <path_to_registry_file> -out <output_dir> [-g]
```

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
