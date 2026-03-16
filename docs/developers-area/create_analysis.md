---
icon: lucide/test-tubes
title: "New analysis"
tags:
    - development
    - plugins
    - inputs
---

# Creating a New Analysis

The SCT framework uses a **plugin-based architecture** for analyses. Each analysis:

- Registers itself into the global ``ANALYSIS_REGISTRY``
- Optionally exposes a ``Typer CLI command`` (or command group)
- Provides its configuration class
- Optionally provides testing hooks

All analyses are automatically discovered and registered at runtime.

> :lucide-circle-chevron-right: Refer to the [analyses documentation](../documentation/analyses/index.md) for more details on analyses architecture and implementation structure.

## 1. Implement the Analysis Logic

Create your core implementation in ``main.py``. This function should provide a full execution pipeline, starting from
product path up to generating results and saving those to disk (graphs included, if needed):

```python title="main.py"
def full_analysis_function(product, output_directory, config):
    # analysis logic here
    pass
```

## 2. Implement the CLI Command

Create ``cli.py``.

You may define:

• A single command  
• A command group with subcommands  

### Example — Single Command

```python title="cli.py"
import typer
from sct.cli import common

def analysis_name_cli(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
    ...  # other arguments, if needed
):
    from .main import run_analysis_name
    run_analysis_name(product, output_directory)
```

### Example — Group with Subcommands

```python title="cli.py"
import typer
group_app = typer.Typer(help="Analysis group.")

@group_app.command("first-analysis")
def first_analysis(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
) -> None:
    ...

@group_app.command("second-analysis")
def second_analysis(
    ctx: typer.Context,
    product: common.InputProductOption,
    output_directory: common.OutputDirectoryOption,
    graphs: common.GraphsOption = False,
) -> None:
    ...
```

If you register a group, all subcommands are automatically available.

## 3. Implement the Configuration Class

Each analysis must provide a configuration class implementing ``sct.configuration.config_abc.AnalysisConfigABC``.

```python title="config.py"

from dataclasses import dataclass
from sct.config.config_abc import AnalysisConfigABC

@dataclass
class AnalysisNameConfig(AnalysisConfigABC):

    @classmethod
    def from_dict(cls, arg: dict):
        return cls()

    def to_dict(self) -> dict:
        return {}
```

The base class already provides:

- ``from_toml()``
- ``to_toml()``

Only ``from_dict`` and ``to_dict`` must be implemented.

## 4. Register the Analysis

Add the following code to the ``__init__.py`` file of the new analysis module.

```python title="__init__.py"
from sct.core.base import AnalysisHandler, AnalysisTestingHandler
from sct.core.registry import register_analysis
from .cli import analysis_name_cli
from .config import AnalysisNameConfig

ANALYSIS_NAME = __name__.split(".")[-1]  # name taken from __name__ of the module

register_analysis(
    analysis_type=ANALYSIS_NAME,
    handler=AnalysisHandler(
        config=AnalysisNameConfig,
        cli_command=analysis_name_cli,  # optional
        testing=AnalysisTestingHandler(  # optional
            api_runner=run_analysis_name_api,
            cli_runner=run_analysis_name_cli,
            validator=validate_analysis_name_results,
        ),
    ),
)
```

Important:

- Register the **Click group** if your analysis has subcommands.
- Do NOT register subcommands individually.

## 5. Automatic Discovery

The framework automatically loads all analyses via `#!python sct.analyses.load_analyses()`.

This imports all submodules under ``sct.analyses`` and triggers their registration.

You **do not need** to manually modify:

- ``sct/analyses/__init__.py``
- the main CLI file

## 6. CLI Integration

All registered CLI commands are automatically attached to the root ``sct`` CLI group.

If you registered:

A single command:

```bash title="CLI command"
sct analysis-name-cli ...
```

A group:

```bash title="CLI command"
sct analysis-name-group first-analysis ...
sct analysis-name-group second-analysis ...
```

## 7. Optional Testing Hooks

If your analysis supports CLI/API validation, provide a testing handler:

```python title="__init__.py"
from sct.core.base import AnalysisTestingHandler

testing=AnalysisTestingHandler(
    api_runner=run_api,
    cli_runner=run_cli,
    validator=validate_results,
)
```

This enables integration with the automated test framework.

## Best Practices

- [x] Register only once  
- [x] Register the group, not subcommands  
- [x] Keep registration inside the analysis module  
- [x] Do not modify the root CLI file  
- [x] Avoid global side effects outside registration  

## Common Mistakes

❌ Registering subcommands instead of the group  
❌ Forgetting to implement ``to_dict`` / ``from_dict``  
❌ Importing analyses manually instead of using auto-discovery  
❌ Leaving file log handlers open in CLI commands
