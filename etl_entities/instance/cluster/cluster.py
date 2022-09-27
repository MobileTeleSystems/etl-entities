#  Copyright 2022 MTS (Mobile Telesystems)
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

import re

from pydantic import StrictStr


class Cluster(StrictStr):
    """Cluster representation

    Cluster name should be in format ``somecluster``, ``some-cluster``, ``some-cluster``.

    .. warning::

        Name can have only alphanumeric symbols and ``-``, ``_``.

        Name cannot be just a numeric value, prefer ``somecluster-001``.

    Examples
    ----------

    .. code:: python

        from etl_entities import Cluster

        cluster = Cluster("some-cluster")
    """

    regex = re.compile("^[a-zA-Z]+([a-zA-Z-_]*[a-zA-Z0-9])*$")
