# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Command Line Interface for SCT Info feature."""

from __future__ import annotations

import importlib.metadata
import json
import urllib.request
import xmlrpc.client
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from sct import __version__
from sct.plugins import available_plugins

CORE_DEPENDENCIES = [
    "perseo-quality",
    "perseo-perturbations",
    "perseo-core",
]

console = Console()


def list_pypi_projects(username="aresys"):
    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    return sorted(name for role, name in client.user_packages(username))


def get_latest_version(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        return data["info"]["version"]
    except Exception:
        return "unknown"


info_app = typer.Typer(
    help="Display SCT info about analyses, plugins, and dependencies.",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)


@info_app.callback(invoke_without_command=True)
def info(
    ctx: typer.Context,
    available_plugins_flag: Annotated[
        bool,
        typer.Option(
            "--available-plugins",
            help="Also fetch available SCT plugins from PyPI",
        ),
    ] = False,
) -> None:
    console.print(f"[bold]SCT version:[/] [cyan]{__version__}[/]")
    console.print()

    table = Table(title="Core Dependencies", title_style="bold")
    table.add_column("Package", style="cyan")
    table.add_column("Version")
    for dep in CORE_DEPENDENCIES:
        try:
            version = importlib.metadata.version(dep)
        except importlib.metadata.PackageNotFoundError:
            version = "not installed"
        table.add_row(dep, version)
    console.print(table)
    console.print()

    table = Table(title="Installed Plugins", title_style="bold")
    table.add_column("Plugin", style="cyan")
    table.add_column("Version")
    if available_plugins:
        for plugin in available_plugins:
            table.add_row(plugin.__name__, plugin.version)
    else:
        table.add_row("(none installed)", "")
    console.print(table)
    console.print()

    if available_plugins_flag:
        projects = list_pypi_projects("aresys")
        sct_plugins = [p for p in projects if p.startswith("sct-")]

        table = Table(title="Available SCT Plugins on PyPI", title_style="bold")
        table.add_column("Package", style="cyan")
        table.add_column("Latest", justify="right")
        table.add_column("Installed")

        with console.status("Fetching versions from PyPI..."):
            for pkg in sct_plugins:
                latest = get_latest_version(pkg)
                try:
                    installed = importlib.metadata.version(pkg)
                except importlib.metadata.PackageNotFoundError:
                    installed = "[dim]not installed[/]"
                table.add_row(pkg, f"v{latest}", installed)

        console.print(table)
