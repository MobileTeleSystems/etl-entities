# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import os

from etl_entities.plugins import import_plugins
from etl_entities.version import __version__

__all__ = ["__version__"]


def plugins_auto_import():
    """
    Automatically import all ETL entities plugins.

    Executed while etl_entities is being imported.

    See :ref:`plugins` documentation.
    """
    plugins_enabled = os.getenv("ETL_ENTITIES_PLUGINS_ENABLED", "true").lower() != "false"
    if not plugins_enabled:
        return

    plugins_whitelist = list(filter(None, os.getenv("ETL_ENTITIES_PLUGINS_WHITELIST", "").split(",")))
    plugins_blacklist = list(filter(None, os.getenv("ETL_ENTITIES_PLUGINS_BLACKLIST", "").split(",")))

    import_plugins("etl_entities.plugins", whitelist=plugins_whitelist, blacklist=plugins_blacklist)


plugins_auto_import()
