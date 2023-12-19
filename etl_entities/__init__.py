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
