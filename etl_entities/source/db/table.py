# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import re
from typing import Union

import typing_extensions

try:
    from pydantic.v1 import ConstrainedStr
except (ImportError, AttributeError):
    from pydantic import ConstrainedStr  # type: ignore[no-redef, assignment]

from etl_entities.entity import BaseModel, Entity
from etl_entities.instance import Cluster, GenericURL


# table or db name cannot have delimiters used in qualified_name
class TableDBName(ConstrainedStr):
    regex = re.compile("^[^@#]+$")


@typing_extensions.deprecated(
    "Deprecated in v2.0, will be removed in v3.0",
    category=UserWarning,
)
class Table(BaseModel, Entity):
    """DB table representation

    .. deprecated:: 2.0.0

    Parameters
    ----------
    name : str

        Table name

        .. warning::

            Cannot contain ``.``, ``@`` and ``#``

    db : str

        Database (schema) name

        .. warning::

            Cannot contain dot symbol ``.``, ``@`` and ``#``

    instance : :obj:`etl_entities.instance.url.generic_url.GenericURL`
                or :obj:`etl_entities.instance.cluster.cluster.Cluster`

        Cluster name in format ``my-cluster`` or instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    --------

    .. code:: python

        from etl_entities import Table

        table1 = Table(name="mydb.mytable", instance="postgres://db.host:5432")
        table2 = Table(name="mydb.mytable", instance="rnd-dwh")
    """

    name: TableDBName
    instance: Union[GenericURL, Cluster]

    @property
    def full_name(self) -> str:
        """
        Full name of table

        Returns
        -------
        value : str

            Table full name

        Examples
        --------

        .. code:: python

            from etl_entities import Table

            table = Table(name="mydb.mytable", instance="postgres://db.host:5432")

            assert table.full_name == "mydb.mytable"
        """

        return self.name

    def __str__(self):
        """
        Returns full table name
        """

        return self.full_name

    @property
    def qualified_name(self) -> str:
        """
        Unique name of table

        Returns
        -------
        value : str

            Qualified name

        Examples
        --------

        .. code:: python

            from etl_entities import Table

            table1 = Table(name="mydb.mytable", instance="postgres://db.host:5432")
            table2 = Table(name="mydb.mytable", instance="rnd-dwh")

            assert table1.qualified_name == "mydb.mytable@postgres://db.host:5432"
            assert table2.qualified_name == "mydb.mytable@rnd-dwh"
        """

        return "@".join([str(self), str(self.instance)])
