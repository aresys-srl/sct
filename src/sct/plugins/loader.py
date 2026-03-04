# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Input Products plugins loader
-----------------------------
"""

from __future__ import annotations

from functools import partial
from typing import Type

from stevedore import ExtensionManager

from sct.configuration.logger import sct_logger
from sct.plugins.protocols import InputProductPluginProtocol


def import_plugins(
    *,
    plugin_protocol: Type,
    namespace: str,
) -> list:
    """
    Load plugins using Stevedore entry points.

    Parameters
    ----------
    plugin_protocol : Type
        Protocol that plugins must satisfy
    namespace : str
        Entry-point namespace

    Returns
    -------
    list
        list of available plugins
    """

    sct_logger.debug("Plugin discovery started")

    manager = ExtensionManager(
        namespace=namespace,
        invoke_on_load=True,
        on_load_failure_callback=_on_load_failure,
    )

    valid_plugins = []

    for extension in manager:
        plugin = extension.plugin

        if isinstance(plugin, plugin_protocol):
            valid_plugins.append(plugin)
            sct_logger.debug(f"Loaded plugin: {extension.name}")
        else:
            sct_logger.warning(f"{extension.name} rejected: does not satisfy protocol {plugin_protocol.__name__}")

    sct_logger.debug("Plugin discovery completed")
    sct_logger.info("Available plugins:")
    for plugin in valid_plugins:
        sct_logger.info(f" - {plugin.__name__} v {plugin.version}")

    return valid_plugins


def _on_load_failure(manager, entrypoint, exc):
    sct_logger.error(f"Failed loading plugin {entrypoint.name}: {exc}")


import_input_product_plugins = partial(
    import_plugins,
    plugin_protocol=InputProductPluginProtocol,
    namespace="sct.input_products",
)
