---
icon: lucide/wrench
title: "Usage"
tags:
    - point target analysis
    - tutorials
    - CLI
    - python
    - testing
---

# Running a Point Target Analysis

Here is a detailed description on how to execute a Point Target Analysis with SCT in three ways:

1. From the [__Command Line Interface (CLI)__](#cli-analysis)  → user-facing execution
2. From the [__Python API__](#api-analysis)  → programmatic/scripting/orchestration integration
3. From the [__Testing Interface__](#testing-analysis)  → automated validation

!!! info "Prerequisites"

    - SCT must be installed
    - A valid product must be available and [its format plugin installed](../../../format_plugins.md)
    - A configuration file in TOML format (optional)
    - A testing registry (optional)

## From CLI {#cli-analysis}

Point target analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

```bash title="CLI command"
sct [--config <path_to_config>] point_target -p <product_path> -out <output_dir> \
    -pt <point_target_file_path> [-eo <path>] [-ec <path>] [-g]
```

where ``-g`` is used to enable graphs generation (if added to the command), ``-eo`` is used to specify the path to the
external orbit file, ``-ec`` is used to specify the path to the external corrections product (i.e. ETAD products for Sentinel-1).

!!! info "External Point Targets Data"

    The external source of point targets data provided as a .csv file must be compliant with the template that can be downloaded
    from the resources folder on GitHub.  
    > :lucide-circle-chevron-right: Refer to the [related documentation](../../point_targets.md) for more details.

## From Python API {#api-analysis}

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

```python linenums="1" title="Python API"

from pathlib import Path
from sct.analyses.point_target.main import full_point_target_analysis
from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig

# this is the default, but parameters can be set here
config = SCTPointTargetAnalysisConfig()

csv_results_path = full_point_target_analysis(
    product=Path("path/to/product"),
    point_target_source=Path("path/to/point_target_source.csv"),
    output_directory=Path("path/to/output_directory"),
    config=config,  # optional, can be None
    graphs=True,  # optional, can be False
)
```

## From Testing Interface {#testing-analysis}

This analysis also provides a testing interface, which can be used to run the analysis from the SCT Testing Framework. To
do so, a registry .json file containing test cases must be created and provided to the testing CLI interface.

```json title="testing_registry.json"
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
```

Then the testing CLI interface can be used as follows:

```bash title="Testing Interface"
sct testing test -r <path_to_registry_file> -out <output_dir> [-g]
```

When a ``reference_output`` is provided, the testing CLI interface will compare the results with the reference output
and report any discrepancy.
