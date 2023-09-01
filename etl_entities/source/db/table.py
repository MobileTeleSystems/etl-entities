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

import re
from typing import Union

from pydantic import ConstrainedStr

from etl_entities.entity import BaseModel, Entity
from etl_entities.instance import Cluster, GenericURL


# table or db name cannot have delimiters used in qualified_name
class TableDBName(ConstrainedStr):
    regex = re.compile("^[^@#]+$")


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

    instance : :obj:`etl_entities.instance.url.generic_url.GenericURL`
                or :obj:`etl_entities.instance.cluster.cluster.Cluster`

        Cluster name in format ``my-cluster`` or instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

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
        ----------
        value : str

            Table full name

        Examples
        ----------

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
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import Table

            table1 = Table(name="mydb.mytable", instance="postgres://db.host:5432")
            table2 = Table(name="mydb.mytable", instance="rnd-dwh")

            assert table1.qualified_name == "mydb.mytable@postgres://db.host:5432"
            assert table2.qualified_name == "mydb.mytable@rnd-dwh"
        """

        return "@".join([str(self), str(self.instance)])
