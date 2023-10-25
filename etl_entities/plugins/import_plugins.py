#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

import inspect
import logging
import textwrap

from importlib_metadata import EntryPoint, entry_points

from etl_entities.version import __version__

log = logging.getLogger(__name__)


def _prepare_error_msg(plugin_name: str, package_name: str, package_version: str, package_value: str):
    failed_import = package_value.split(":")
    if len(failed_import) > 1:
        import_statement = f"from {failed_import[0]} import {failed_import[1]}"
    else:
        import_statement = f"import {failed_import[0]}"

    return textwrap.dedent(
        f"""
        Error while importing plugin {plugin_name!r} from package {package_name!r} v{package_version}.

        Statement:
            {import_statement}

        Check if plugin is compatible with current etl_entities version {__version__}.

        You can disable loading this plugin by setting environment variable:
            ETL_ENTITIES_PLUGINS_BLACKLIST='{plugin_name},failing-plugin'

        You can also define a whitelist of packages which can be loaded by etl_entities:
            ETL_ENTITIES_PLUGINS_WHITELIST='not-failing-plugin1,not-failing-plugin2'

        Please take into account that plugin name may differ from package or module name.
        See package metadata for more details
        """,
    ).strip()


def import_plugin(entrypoint: EntryPoint):
    """
    Import a specific entrypoint.

    If any exception is raised during import, it will be wrapped with ImportError
    containing all diagnostic information about entrypoint.
    """
    try:
        loaded = entrypoint.load()
        log.debug("Successfully loaded plugin %r", entrypoint.name)
        log.debug("  source = %r", inspect.getfile(loaded))
    except Exception as e:
        error_msg = _prepare_error_msg(
            plugin_name=entrypoint.name,
            package_name=entrypoint.dist.name if entrypoint.dist else "unknown",
            package_version=entrypoint.dist.version if entrypoint.dist else "unknown",
            package_value=entrypoint.value,
        )
        raise ImportError(error_msg) from e


def import_plugins(group: str, whitelist: list[str] | None = None, blacklist: list[str] | None = None):  # noqa: WPS213
    """
    Import all plugins registered for ETL entities.
    """
    log.debug("Searching for plugins with group %r", group)

    entrypoints = entry_points(group=group)
    plugins_count = len(entrypoints)

    if not plugins_count:
        log.debug("|Plugins| No plugins registered")
        return

    log.debug("|Plugins| Found %d plugins", plugins_count)
    log.debug("|Plugins| Plugin load options:")
    log.debug("whitelist", whitelist or [])
    log.debug("blacklist", blacklist or [])

    for i, entrypoint in enumerate(entrypoints):
        if whitelist and entrypoint.name not in whitelist:
            log.info("Skipping plugin %r because it is not in whitelist", entrypoint.dist.name)
            continue

        if blacklist and entrypoint.name in blacklist:
            log.info("Skipping plugin %r because it is in a blacklist", entrypoint.dist.name)
            continue

        if log.isEnabledFor(logging.DEBUG):
            log.debug("Loading plugin (%d of %d):", i + 1, plugins_count)
            log.debug("    name = %r", entrypoint.name)
            log.debug("    package = %r", entrypoint.dist.name)
            log.debug("    version = %r", entrypoint.dist.version)
            log.debug("    importing = %r", entrypoint.value)
        else:
            log.info("Loading plugin %r", entrypoint.name)

        import_plugin(entrypoint)
