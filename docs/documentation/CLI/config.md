---
icon: lucide/sliders-horizontal
title: "Configuration"
tags:
    - configuration
    - CLI
    - python
    - toml
    - inputs
---

# Configuration file setup for CLI tool

The SCT Command Line Interface (CLI) tool let the user perform quality analyses on input products using the SCT Python
package as a command line executable software. All the registered analyses have a dedicated command that can be specified
to perform the operation of choice. Refer to the [available analyses](../analyses/index.md) for further information.

This commands have been developed to be run with a minimal setup and only the essential parameters to be specified, such
as input and output folders.
For an in-depth documentation on how to use the command line tool, please refer [to this page](index.md).

Nevertheless, a configuration file (TOML format) can be provided as input to tweak and tune several options and parameters
in order to fully customize each analysis.

This configuration file is designed to work with optional sections that can be specified only if that specific feature should
be altered with respect to the default behavior. In principle, if all default settings are enough for the user, this
configuration file is not necessary.

!!! danger "Validation"

    Configuration files are validated through a JSON schema when provided as input for the tool to assess compliance.

## Configuration file

The .toml configuration file is organized in sections and subsections related to specific analyses.
*Every section is optional*, and should be added only if default parameters for a specific analysis are not sufficient
for the user.

The available sections of this configuration file are:

- **general**: the highest level of configuration, not related to a specific feature.

- **analyses_sections**: sections that can be used to access specific analysis configurations and parameters. Each analysis implements its own configuration section.

> :lucide-circle-chevron-right: Refer to the [analyses documentation](../analyses/index.md) for more details on each analysis and its configuration section.

General Configuration
^^^^^^^^^^^^^^^^^^^^^

The following parameters can be configured directly under the `general` section.

```toml title="General Configuration"
[general]
save_log = true                 # save analysis log to output folder
save_config_copy = true         # save analysis config to output folder
```
