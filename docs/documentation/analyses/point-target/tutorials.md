---
icon: lucide/book-type
title: "Tutorials"
tags:
    - point target analysis
    - tutorials
    - python
    - configuration
---

# Quick Start & Tutorials

This section provides a focused collection of practical examples to help you get started with the Point Target analysis
in SCT. The tutorials demonstrate how to perform common tasks both through the command-line interface (CLI) and by using
SCT as a Python library.

Each example walks through a specific workflow step-by-step, highlighting recommended practices and typical use cases.
By following these guides, you will quickly learn how to configure and run this analysis.

Use this section as your starting point for understanding and applying the Point Target workflow effectively.

## Basic usage

Point Target Analysis can be performed using CLI or Python API, as described in the [usage documentation](usage.md).

## Advanced usage

Here are some advanced usage examples that you can use as a starting point.

### Optional Inputs

The following inputs are optional and can be used to customize the analysis:

- **External Orbit File**: used to compute ionospheric and tropospheric perturbations
- **External Corrections Product**: used to compute ionospheric and tropospheric perturbations

These inputs can be provided to the CLI tool using the `--external-orbit/-eo` and `--external-corrections/-ec` options,
respectively.

!!! tip "Optional Inputs"

    As of now, only *Sentinel-1* plugin supports External Orbits files (.EOF format) and External Corrections products (i.e. ETAD products).

The exact same thing can be done from a custom script using SCT as a library:

```python linenums="1"

from pathlib import Path
from sct.analyses.point_target.main import full_point_target_analysis
from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig

# this is the default, but parameters can be set here
config = SCTPointTargetAnalysisConfig()

csv_results_path = full_point_target_analysis(
    product=Path("path/to/product"),
    point_target_source=Path("path/to/point_target_source.csv"),
    output_directory=Path("path/to/output_directory"),
    external_orbit=Path("path/to/external_orbit_file"),  # optional, can be None
    external_corrections_product=Path("path/to/corrections_product"),  # optional, can be None
    config=config,  # optional, can be None
    graphs=True,  # optional, can be False
)
```

### Ionospheric and Tropospheric Maps

Input configuration file must contain the following lines to be able to perform a Point Target Analysis taking into account
atmospheric perturbations from external maps.

```toml

# both or just one of the two perturbations can be selected
[point_target_analysis.corrections]
enable_ionospheric_correction = true
enable_tropospheric_correction = true

[point_target_analysis.corrections.ionosphere]
ionospheric_maps_directory = "path/to/ionospheric/maps/directory"
ionospheric_analysis_center = "cor"

[point_target_analysis.corrections.troposphere]
tropospheric_maps_directory = "path/to/tropospheric/maps/directory"
tropospheric_map_grid_resolution = "fine"
```

Then simply run the analysis as described in the previous section providing the path to the configuration file.

```bash
sct --config path_to_config_toml point-target-analysis ...
```

```python linenums="1"

from sct.analyses.point_target.config import SCTPointTargetAnalysisConfig

config = SCTPointTargetAnalysisConfig.from_toml("path/to/config.toml")

...
```

!!! tip "Maps Download"

    The ionospheric and tropospheric maps can be downloaded directly using the dedicated CLI utility commands.  
    > :lucide-circle-chevron-right: Refer to the [CLI utility commands](../../../documentation/CLI/cli_utilities.md) for more details.
