.. _add_analysis:

Adding a New Analysis
=====================

Overview
--------

The SCT framework uses a **plugin-based architecture** for analyses. Each analysis:

- Registers itself into the global ``ANALYSIS_REGISTRY``
- Optionally exposes a ``Click CLI command`` (or command group)
- Provides its configuration class
- Optionally provides testing hooks

All analyses are automatically discovered and registered at runtime.

Analysis architecture and implementation structure are defined in the :ref:`following section <sct_analyses>`.

Step 1 — Implement the Analysis Logic
--------------------------------------

Create your core implementation in ``main.py``. This function should provide a full execution pipeline, starting from
product path up to generating results and saving those to disk (graphs included, if needed):

.. code-block:: python

    def full_analysis_function(product, output_directory, config):
        # analysis logic here
        pass


Step 2 — Implement the CLI Command
-----------------------------------

Create ``cli.py``.

You may define:

• A single command  
• A command group with subcommands  

Example — Single Command
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import click
    from pathlib import Path

    @click.command(name="my-analysis")
    @click.option("--product", type=click.Path(path_type=Path))
    @click.option("--output-directory", type=click.Path(path_type=Path))
    def analysis_name_cli(product: Path, output_directory: Path):
        """My custom analysis."""
        from .main import run_analysis_name
        run_analysis_name(product, output_directory)


Example — Group with Subcommands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import click

    @click.group(name="my-analysis")
    def analysis_name_cli():
        """Grouped analysis."""

    @analysis_name.command("mode-a")
    def mode_a():
        pass

    @analysis_name.command("mode-b")
    def mode_b():
        pass

If you register a group, all subcommands are automatically available.


Step 3 — Implement the Configuration Class
-------------------------------------------

Each analysis must provide a configuration class implementing :py:class:`sct.configuration.config_abc.AnalysisConfigABC`.

Example:

.. code-block:: python

    from dataclasses import dataclass
    from sct.config.config_abc import AnalysisConfigABC

    @dataclass
    class AnalysisNameConfig(AnalysisConfigABC):

        @classmethod
        def from_dict(cls, arg: dict):
            return cls()

        def to_dict(self) -> dict:
            return {}

The base class already provides:

- ``from_toml()``
- ``to_toml()``

Only ``from_dict`` and ``to_dict`` must be implemented.


Step 4 — Register the Analysis
-------------------------------

In ``sct/analyses/analysis_name/__init__.py``:

.. code-block:: python

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

Important:

- Register the **Click group** if your analysis has subcommands.
- Do NOT register subcommands individually.


Step 5 — Automatic Discovery
-----------------------------

The framework automatically loads all analyses via:

.. code-block:: python

    sct.analyses.load_analyses()

This imports all submodules under ``sct.analyses`` and triggers their registration.

You do NOT need to manually modify:

- ``sct/analyses/__init__.py``
- the main CLI file


Step 6 — CLI Integration
------------------------

All registered CLI commands are automatically attached to the root ``sct`` CLI group.

If you registered:

• A single command:

    .. code-block:: bash

        sct my-analysis ...

• A group:

    .. code-block:: bash

        sct my-analysis mode-a ...
        sct my-analysis mode-b ...


Step 7 — Optional Testing Hooks
--------------------------------

If your analysis supports CLI/API validation, provide a testing handler:

.. code-block:: python

    from sct.core.base import AnalysisTestingHandler

    testing=AnalysisTestingHandler(
        api_runner=run_api,
        cli_runner=run_cli,
        validator=validate_results,
    )

This enables integration with the automated test framework.


Best Practices
--------------

✔ Register only once  
✔ Register the group, not subcommands  
✔ Keep registration inside the analysis module  
✔ Do not modify the root CLI file  
✔ Avoid global side effects outside registration  

Common Mistakes
---------------

❌ Registering subcommands instead of the group  
❌ Forgetting to implement ``to_dict`` / ``from_dict``  
❌ Importing analyses manually instead of using auto-discovery  
❌ Leaving file log handlers open in CLI commands  


Summary
-------

To create a new analysis:

1. Create folder under ``sct/analyses/``
2. Implement logic
3. Implement CLI command/group
4. Implement config class
5. Register in ``__init__.py``
6. Done — it is auto-discovered
