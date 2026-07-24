# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Command line interface tool for SCT.

### Design choices

The root command group is a ``LazyGroup`` (a ``RichGroup`` subclass) that
defers subcommand loading until invocation.  This keeps ``import sct``,
``sct --version``, ``sct --help`` and ``sct info`` fast, *without* importing the
scientific stack (``perseo``, ``numpy``, …) or any analysis implementation.

Subcommands are **still written as ``typer.Typer`` apps**. The bridge function
``_typer_to_click`` converts them to ``click.Command`` objects at load time so
they plug into the lazy group.
This avoids a rewrite of every subcommand while enabling deferred imports.

!!! note

    ``typer.Typer`` does not expose a hook to intercept subcommand resolution:
    commands are registered eagerly via ``add_typer()``.  Subclassing
    ``RichGroup`` (which inherits from ``click.Group``) gives
    ``get_command()`` / ``list_commands()`` override points, which is what makes
    true lazy loading possible.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Callable

import click
from rich_click import RichGroup

from sct import __version__ as VERSION

ANALYSIS_ENTRY_POINT_GROUP = "sct.analyses"


class _DeferredCommand(click.Command):
    """A command placeholder that defers loading until first use.

    ``RichGroup.format_options()`` calls ``get_command()`` for every subcommand
    during help rendering.  This wrapper satisfies that call with a real
    ``click.Command`` that has ``name`` and ``short_help`` (all that's needed
    for rendering), but delays ``_typer_to_click()`` (and the heavy imports it
    triggers) until the command is actually invoked.
    """

    def __init__(self, name: str, short_help: str, loader: Callable[[], click.Command]) -> None:
        super().__init__(name, short_help=short_help)
        self._loader = loader

    @property
    def _real_command(self) -> click.Command:
        if (real := getattr(self, "_real_cmd", None)) is None:
            real = self._loader()
            real.name = self.name
            self._real_cmd = real
        return real

    def invoke(self, ctx: click.Context) -> Any:
        return self._real_command.invoke(ctx)

    def make_context(
        self, info_name: str, args: list[str], parent: click.Context | None = None, **extra: Any
    ) -> click.Context:
        return self._real_command.make_context(info_name, args, parent=parent, **extra)


@dataclass
class _LazySubcommand:
    """A subcommand that is imported only when actually needed."""

    loader: Callable[[], click.Command]
    short_help: str

    def load(self, name: str = "") -> click.Command:
        """Return a ``_DeferredCommand`` wrapping the real loader.

        The returned stub has ``name`` and ``short_help`` available immediately
        for rich-click's help rendering, but does *not* invoke the loader until
        ``invoke()`` or ``make_context()`` is called.
        """
        return _DeferredCommand(name=name, short_help=self.short_help, loader=self.loader)


def _typer_to_click(cli_obj, name: str) -> click.Command:
    """Convert a Typer app (group) or a single command callable to a click command.

    Subcommands are written as ``typer.Typer`` apps but the root group is a
    ``click.Group`` subclass (for lazy loading).  This bridge converts the Typer
    object into a ``click.Command`` via ``typer.main.get_command()`` so it can
    be registered as a subcommand of the click root group.
    """
    import typer
    from typer.main import get_command

    if isinstance(cli_obj, typer.Typer):
        command = get_command(cli_obj)
    else:
        wrapper = typer.Typer(add_completion=False)
        wrapper.command(name=name)(cli_obj)
        command = get_command(wrapper)

    command.name = name
    return command


def _fixed_loader(module_path: str, attribute: str, name: str) -> Callable[[], click.Command]:
    def _load() -> click.Command:
        module = importlib.import_module(module_path)
        return _typer_to_click(getattr(module, attribute), name)

    return _load


def _analysis_loader(plugin, name: str) -> Callable[[], click.Command]:
    def _load() -> click.Command:
        return _typer_to_click(plugin.get_cli(), name)

    return _load


def _build_lazy_subcommands() -> dict[str, _LazySubcommand]:
    """Build the lazy subcommand map without importing any heavy implementation."""
    subcommands: dict[str, _LazySubcommand] = {
        "auxiliary": _LazySubcommand(
            _fixed_loader("sct.cli.utilities", "utilities_app", "auxiliary"),
            "SCT auxiliary CLI tools.",
        ),
        "testing": _LazySubcommand(
            _fixed_loader("sct.testing.cli", "testing_app", "testing"),
            "SCT testing interface.",
        ),
        "info": _LazySubcommand(
            _fixed_loader("sct.cli.info", "info_app", "info"),
            "Display SCT info about analyses, plugins and dependencies.",
        ),
    }

    for entry_point in entry_points(group=ANALYSIS_ENTRY_POINT_GROUP):
        try:
            # Loading the plugin class imports only the lightweight plugin module,
            # never the analysis implementation or the scientific stack.
            plugin = entry_point.load()
            short_help = getattr(plugin, "short_help", "")
        except Exception:  # noqa: BLE001 - a broken plugin must not break the whole CLI
            continue
        subcommands[entry_point.name] = _LazySubcommand(
            _analysis_loader(plugin, entry_point.name),
            short_help,
        )

    return subcommands


class LazyGroup(RichGroup):
    """A ``RichGroup`` whose subcommands are resolved (and imported) on demand.

    ``typer.Typer`` registers subcommands eagerly via ``add_typer()``, which
    defeats lazy loading.  By subclassing ``RichGroup`` (which provides the
    rich-click help formatting) we override ``get_command()`` and
    ``list_commands()`` to resolve subcommands only when they are actually
    invoked or listed in help output.

    ``get_command()`` returns a ``_DeferredCommand`` stub that holds only the
    subcommand's ``name`` and ``short_help``; the actual ``typer.Typer``-based
    command object (and all its imports) is materialized on first invocation.

    ``invoke()`` also bridges Typer-forked exception types (``Exit``,
    ``ClickException``) back to click's own exceptions so that
    ``Command.main()`` handles them correctly.
    """

    def __init__(self, *args, lazy_subcommands: dict[str, _LazySubcommand] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.lazy_subcommands = lazy_subcommands or {}

    def invoke(self, ctx: click.Context) -> Any:
        """
        ``typer`` vendors its own copy of ``click`` internals (``typer._click``),
        so its ``Exit`` and ``ClickException`` classes are distinct from
        ``click.exceptions.Exit`` / ``click.exceptions.ClickException``.
        ``LazyGroup.invoke`` catches the Typer variants and re-raises them as the
        corresponding click types so that ``Command.main()`` handles them correctly
        in both CLI and test usage.
        """
        try:
            return super().invoke(ctx)
        except Exception as e:
            if type(e).__module__ == "typer._click.exceptions":
                from typer._click.exceptions import (
                    ClickException as TyperClickException,
                )
                from typer._click.exceptions import (
                    Exit as TyperExit,
                )

                if isinstance(e, TyperExit):
                    raise click.exceptions.Exit(e.exit_code) from e
                if isinstance(e, TyperClickException):
                    e.show()
                    raise SystemExit(e.exit_code) from e
            raise

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(set(super().list_commands(ctx)) | set(self.lazy_subcommands))

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        if cmd_name in self.lazy_subcommands:
            return self.lazy_subcommands[cmd_name].load(cmd_name)
        return super().get_command(ctx, cmd_name)


def _version_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    if value:
        click.echo(VERSION)
        ctx.exit()


@click.group(
    cls=LazyGroup,
    lazy_subcommands=_build_lazy_subcommands(),
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 120},
    help="SCT tool for SAR products quality analysis.",
)
@click.option(
    "--config",
    "-cfg",
    "config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to the configuration file with settings.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_version_callback,
    help="Show CLI version and exit",
)
@click.pass_context
def app(ctx: click.Context, config: Path | None) -> None:
    if ctx.invoked_subcommand == "info":
        return

    from sct.configuration.config import GeneralConfiguration
    from sct.configuration.logger import sct_logger

    if config is None:
        sct_logger.info("Configuration not provided. Using default configuration.")
        ctx.obj = GeneralConfiguration()
    else:
        sct_logger.info(f"Using configuration file: {config}.")
        ctx.obj = GeneralConfiguration.from_toml(config)
