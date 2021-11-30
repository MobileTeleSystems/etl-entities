from __future__ import annotations

import re
from typing import Union

from pydantic import ConstrainedStr

from hwmlib.entity import BaseModel, Entity
from hwmlib.location import Cluster, RemoteURL


# table or db name cannot have delimiters used in qualified_name
class TableDBName(ConstrainedStr):
    regex = re.compile("^[^.@#]+$")


class Table(BaseModel, Entity):
    """DB table representation

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

    instance : :obj:`hwmlib.location.url.remote_url.RemoteURL` or :obj:`hwmlib.location.cluster.cluster.Cluster`

        Cluster name in format ``my-cluster`` or instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

    .. code:: python

        from hwmlib import Table

        table1 = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")
        table2 = Table(name="mytable", db="mydb", instance="rnd-dwh")
    """

    name: TableDBName
    db: TableDBName
    instance: Union[RemoteURL, Cluster]

    def __str__(self):
        """
        Returns table name
        """

        return f"{self.db}.{self.name}"

    @property
    def qualified_name(self) -> str:
        """
        Unique name of table

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from hwmlib import Table

            table1 = Table(name="mytable", db="mydb", instance="postgres://db.host:5432")
            table2 = Table(name="mytable", db="mydb", instance="rnd-dwh")

            assert table1.qualified_name == "mydb.mytable@postgres://db.host:5432"
            assert table2.qualified_name == "mydb.mytable@rnd-dwh"
        """

        return "@".join([str(self), str(self.instance)])
