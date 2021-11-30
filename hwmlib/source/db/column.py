from __future__ import annotations

import re
from typing import OrderedDict

from pydantic import ConstrainedStr, Field

from hwmlib.entity import BaseModel, Entity


# column or partition name cannot have delimiters used in qualified_name
class ColumnName(ConstrainedStr):
    regex = re.compile(r"^[^\|/=@#]+$")


class Column(BaseModel, Entity):
    """DB column representation

    Parameters
    ----------
    name : str

        Table name

        .. warning::

            Cannot contain symbols ``|``, ``/``, ``=``, ``@`` and ``#``

    partition : :obj:`collections.OrderedDict`, default: empty dict

        Partition which column belong to, e.g. ``partcolumn=value1/partcolumn2=value2``

        .. warning::

            Names and values cannot contain symbols ``|``, ``/``, ``=``, ``@`` and ``#``

    Examples
    ----------

    .. code:: python

        from hwmlib import Column

        column1 = Column(name="mycolumn")
        column2 = Column(
            name="mycolumn", partition={"partcolumn": "value1", "partcolumn2": "value2"}
        )
    """

    name: ColumnName
    partition: OrderedDict[ColumnName, ColumnName] = Field(default_factory=OrderedDict)

    def __str__(self):
        """
        Returns column name
        """

        return self.name

    @property
    def qualified_name(self) -> str:
        """
        Unique name of column

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from hwmlib import Table

            column1 = Column(name="mycolumn")
            column2 = Column(
                name="mycolumn", partition={"partcolumn": "value1", "partcolumn2": "value2"}
            )

            assert column1.qualified_name == "mycolumn|partcolumn1=value1/partcolumn2=value2"
            assert column2.qualified_name == "mycolumn"
        """

        if self.partition:
            partition_kv = [f"{k}={v}" for k, v in self.partition.items()]
            return f"{self}|{'/'.join(partition_kv)}"

        return str(self)
