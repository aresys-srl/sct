---
icon: material/console
title: "CLI"
tags:
    - CLI
    - analysis
---

# Command Line Interface (CLI)

A command line interface has been developed to be used directly from a shell prompt to access SCT functionalities with an
easy to use approach. All the main functionalities are supported with a dedicated command with its help documentation.

The main command line tool that can be accessed using the ``sct`` command in your favorite shell.

## Main CLI

SCT command line can be invoked in the terminal session as:

```bash title="CLI Entry Point"
sct [--version] [--config/-cfg] [--help/-h]
```

This is the entry point for the console script. The configuration needed to perform the analysis must be provided
using the ``--config/-cfg`` argument. Each installed analysis plugin registers its command automatically under the
``sct`` CLI but the above command alone won't perform any kind of operation.
To select the operation of choice, use the available commands that can be listed using the `--help/-h` option.

!!! tip "Available Analyses"

    Each installed analysis plugin exposes its own dedicated command.  
    > :lucide-circle-chevron-right: Refer to the [analyses plugins documentation site](https://opensource.aresys.it/sct_plugins_analyses/)
    for more details on each analysis and its command.

## SCT Info

The ``info`` command can be used to display information about the installed SCT version, core dependencies, and
list all the available plugins on PyPI.

```bash title="SCT Info"
sct info [--available-plugins]
```

## Testing Interface

A Testing Interface is also available under the ``testing`` CLI group. This feature can be used to run analyses as Test
Cases written into a proper registry .json file.

```bash title="Testing Interface"
sct testing test -r <path_to_registry_file> -out <output_dir> [--cli/-c] [--graphs/-g]
```

where ``--graphs/-g`` is used to enable graphs generation and ``--cli/-c`` is used to enable CLI testing instead of API.

> :lucide-circle-chevron-right: Refer to the [analyses plugins documentation site](https://opensource.aresys.it/sct_plugins/) for more details on each analysis and its testing interface, if any.

## Auxiliary utilities

Another set of companion utilities has been developed and added under the ``auxiliary`` CLI group.

> :lucide-circle-chevron-right: Refer to the [cli utilities documentation](cli_utilities.md) for more details.