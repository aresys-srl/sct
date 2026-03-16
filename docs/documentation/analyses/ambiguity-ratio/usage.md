---
icon: lucide/wrench
title: "Usage"
tags:
    - ambiguity ratio analysis
    - ptar
    - tutorials
    - CLI
    - python
---

# Running a Point Target Ambiguity Ratio Analysis

Here is a detailed description on how to execute an Interferometric Analysis with SCT in three ways:

1. From the [__Command Line Interface (CLI)__](#cli-analysis)  → user-facing execution
2. From the [__Python API__](#api-analysis)  → programmatic/scripting/orchestration integration

!!! info "Prerequisites"

    - SCT must be installed
    - A valid product must be available and [its format plugin installed](../../../format_plugins.md)
    - A configuration file in TOML format (optional)
    - A testing registry (optional)

## From CLI {#cli-analysis}

PTAR analysis can be performed using the following command just specifying the input product and the output directory.
Obviously, an external file containing point targets locations and data must be provided in order to properly run the analysis.

```bash title="CLI command"
sct [--config <path_to_config>] ambiguity_ratio -p <product_path> -out <output_dir> -pt <point_target_file_path>
```

!!! info "External Point Targets Data"

    The external source of point targets data provided as a .csv file must be compliant with the template that can be downloaded
    from the resources folder on GitHub.  
    > :lucide-circle-chevron-right: Refer to the [related documentation](../../point_targets.md) for more details.

## From Python API {#api-analysis}

This analysis is also available directly from Python without using the CLI, and can be imported in any python script
and executed as follows:

```python linenums="1" title="Python API"
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
```
