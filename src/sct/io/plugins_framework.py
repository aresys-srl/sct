# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Plugins framework
-----------------
"""

import importlib
import importlib.util
import pkgutil
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


def get_list_of_valid_plugins(plugins: list[ModuleType], plugin_protocol: type) -> list[ModuleType]:
    """Filter out invalid plugins"""
    invalid_plugins = filter(lambda plugin: not isinstance(plugin, plugin_protocol), plugins)
    for plugin in invalid_plugins:
        sct_logger.warning(
            f"{plugin.__name__} plugin removed from plugin list: "
            + f"does not satisfy the plugin interface: {plugin_protocol}"
        )

    return list(filter(lambda plugin: isinstance(plugin, plugin_protocol), plugins))


def import_plugins(*, plugin_protocol: type, plugin_prefix: str, additional_plugins: list[str]) -> list[ModuleType]:
    """Import plugins that must be importable and satisfy plugin_protocol interface.

    Parameters
    ----------
    plugin_protocol : type
        protocol that plugins must satisfy
    plugin_prefix : str
        string prefix to find plugins
    additional_plugins : list[str]
        list of additional plugins as strings: either absolute paths or importable python modules
    """
    plugins = additional_plugins + [name for _, name, _ in pkgutil.iter_modules() if name.startswith(plugin_prefix)]

    sct_logger.info("Plugin discovery started")
    load_plugins: list[ModuleType] = [
        loaded_plugin for loaded_plugin in (load_plugin(plugin) for plugin in plugins) if loaded_plugin is not None
    ]

    valid_plugins = get_list_of_valid_plugins(
        [plugin for plugin in load_plugins if plugin is not None], plugin_protocol
    )

    sct_logger.info("Plugin discovery completed")
    sct_logger.info("Available plugins:")
    for plugin in valid_plugins:
        sct_logger.info(f" - {plugin.__name__}")
    return valid_plugins
