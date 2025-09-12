# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Plugins utilities
-----------------
"""

import importlib
import importlib.util
from pathlib import Path
from types import ModuleType

from sct.configuration.logger import sct_logger


def _core_load_from_path(plugin: str) -> ModuleType:
    """Core loading module functionality"""
    plugin_path = Path(plugin)
    spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
    if spec is None:
        raise RuntimeError(f"Cannot load {plugin}")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_plugin(plugin: str) -> ModuleType | None:
    """Load a plugin, returns None on failure"""
    try:
        if plugin.endswith(".py"):
            module = _core_load_from_path(plugin)
        else:
            module = importlib.import_module(plugin)
    except (ModuleNotFoundError, RuntimeError, FileNotFoundError) as exc:
        sct_logger.warning(f"Loading of {plugin} failed: {exc}")
    else:
        sct_logger.info(f"Loading of {plugin} successful")
        return module
    return None


def get_list_of_valid_plugins(plugins: list, plugin_protocol: type) -> list:
    """Filter out invalid plugins"""
    invalid_plugins = filter(lambda plugin: not isinstance(plugin, plugin_protocol), plugins)
    for plugin in invalid_plugins:
        sct_logger.warning(
            f"{plugin.__name__} plugin removed from plugin list: "
            + f"does not satisfy the plugin interface: {plugin_protocol}"
        )

    return list(filter(lambda plugin: isinstance(plugin, plugin_protocol), plugins))


def import_plugins(plugins: list[str], plugin_protocol: type, built_in_plugins: list) -> list:
    """Import plugins in the list, they must be importable and satisfy plugin_protocol interface"""
    if not plugins:
        return built_in_plugins

    sct_logger.info("Plugin discovery started")
    discovered_plugins: list[ModuleType | None] = [load_plugin(plugin) for plugin in plugins]
    valid_discovered_plugins = get_list_of_valid_plugins(
        [plugin for plugin in discovered_plugins if plugin is not None], plugin_protocol
    )

    available_plugins = built_in_plugins + valid_discovered_plugins
    sct_logger.info("Plugin discovery completed")
    sct_logger.info("Available plugins:")
    for plugin in available_plugins:
        sct_logger.info(f" - {plugin.__name__}")
    return available_plugins
