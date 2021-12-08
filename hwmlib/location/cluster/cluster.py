from __future__ import annotations

import re

from pydantic import StrictStr


class Cluster(StrictStr):
    """Cluster representation

    Cluster name should be in format ``somecluster``, ``some-cluster``, ``some-cluster``.

    .. warning::

        Name can have only alphanumeric symbols and ``-``, ``_``.

        Name cannot be just a numeric value, prefer ``somecluster-001``.

        Name cannot be ``localhost``

    Examples
    ----------

    .. code:: python

        from hwmlib import Cluster

        cluster = Cluster("some-cluster")
    """

    regex = re.compile("^(?!localhost)[a-zA-Z]+([a-zA-Z-_]*[a-zA-Z0-9])*$")
