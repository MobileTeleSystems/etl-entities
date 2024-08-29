# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import re

try:
    from pydantic.v1 import StrictStr
except (ImportError, AttributeError):
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
