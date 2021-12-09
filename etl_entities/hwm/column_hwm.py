from __future__ import annotations

from typing import Generic, Optional, TypeVar

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM
from etl_entities.source import Column, Table

T = TypeVar("T")


class ColumnHWM(HWM, GenericModel, Generic[T]):
    """Column HWM type

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    table : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : int or ``None``, default: ``None``

        HWM value

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from etl_entities import IntHWM, Column, Table

        column = Column(name="id")
        table = Table(name="mytable", db="mydb", location="postgres://db.host:5432")

        hwm = IntHWM(column=column, table=table, value=1)
    """

    column: Column
    table: Table
    value: Optional[T] = None

    @property
    def name(self) -> str:
        """
        HWM column name

        Returns
        ----------
        value : str

            Column name

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM, Column, Table

            column = Column(name="id")
            table = Table(name="mytable", db="mydb", location="postgres://db.host:5432")

            hwm = IntHWM(column=column, table=table, value=1)

            assert hwm.name == "id"
        """

        return self.column.name

    @property
    def qualified_name(self) -> str:
        """
        Unique name of HWM

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import ColumnHWM, Column, Table

            column = Column(name="id")
            table = Table(name="mytable", db="mydb", location="postgres://db.host:5432")

            hwm = IntHWM(column=column, table=table, value=1)

            assert (
                hwm.qualified_name
                == "id#mydb.mytable@postgres://db.host:5432#currentprocess@currenthost"
            )
        """

        return "#".join([self.column.qualified_name, self.table.qualified_name, self.process.qualified_name])

    def with_value(self, value: T | None) -> ColumnHWM:
        if value is not None:
            dct = self.dict()
            dct["value"] = value
            return self.parse_obj(dct)

        return self

    def serialize(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import ColumnHWM

            hwm = ColumnHWM(value=1, ...)
            hwm.serialize()
            # "1"

            hwm = ColumnHWM(value=None, ...)
            hwm.serialize()
            # "null"
        """

        if self.value is None:
            return "null"

        return super().serialize()

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is ``None``, ``True`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import ColumnHWM

            hwm = ColumnHWM(value=1, ...)
            assert hwm  # same as hwm.value is not None

            hwm = ColumnHWM(value=None, ...)
            assert not hwm
        """

        return self.value is not None

    def __add__(self, value):
        """Creates copy of HWM with increased value

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot add ``str`` to ``int`` value, but you can add ``int`` to ``int``.

            ``None`` input does not change the value.

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm1 = IntHWM(value=1, ...)
            hwm2 = IntHWM(value=2, ...)

            assert hwm1 + 1 == hwm2  # same as IntHWM(value=hwm1.value + 1, ...)
        """

        if self.value is not None and value is not None:
            return self.with_value(self.value + value)

        return self

    def __sub__(self, value):
        """Creates copy of HWM with decreased value

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot subtract ``str`` from ``int`` value, but you can subtract ``int`` from ``int``.

            ``None`` input does not change the value.

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm1 = IntHWM(value=1, ...)
            hwm2 = IntHWM(value=2, ...)

            assert hwm1 - 1 == hwm2  # same as IntHWM(value=hwm1.value - 1, ...)
        """

        if self.value is not None and value is not None:
            return self.with_value(self.value - value)

        return self
