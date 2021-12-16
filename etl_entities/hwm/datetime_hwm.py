from __future__ import annotations

from datetime import datetime
from functools import total_ordering
from typing import Optional

from etl_entities.hwm.column_hwm import ColumnHWM
from etl_entities.hwm.hwm import HWM


@total_ordering
class DateTimeHWM(ColumnHWM[datetime]):
    """DateTime HWM type

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    table : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : :obj:`datetime.datetime` or ``None``, default: ``None``

        HWM value

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from datetime import datetime
        from etl_entities import DateTimeHWM, Column, Table

        column = Column(name="id")
        table = Table(name="mytable", db="mydb", location="postgres://db.host:5432")

        hwm = DateTimeHWM(
            column=column,
            table=table,
            value=datetime(year=2021, month=21, day=31, hour=11, minute=22, second=33),
        )
    """

    value: Optional[datetime] = None

    def serialize(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from datetime import datetime
            from etl_entities import DateTimeHWM

            hwm = DateTimeHWM(
                value=datetime(year=2021, month=21, day=31, hour=11, minute=22, second=33), ...
            )
            assert hwm.serialize() == "2021-12-31T11:22:33"

            hwm = DateTimeHWM(value=None, ...)
            assert hwm.serialize() == "null"
        """

        if self.value is None:
            return "null"

        return self.value.isoformat()

    @classmethod
    def deserialize(cls, value: str) -> datetime | None:
        """Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`datetime.datetime` or ``None``

            Deserialized value

        Examples
        ----------

        .. code:: python

            from datetime import datetime
            from etl_entities import DateTimeHWM

            assert DateTimeHWM.deserialize("2021-12-31T11-22-33") == datetime(
                year=2021, month=12, day=31, hour=11, minute=22, second=33
            )

            assert DateTimeHWM.deserialize("null") is None
        """

        value = super().deserialize(value)

        if value.lower() == "null":
            return None

        return datetime.fromisoformat(value)

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.datetime_hwm.DateTimeHWM` or :obj:`datetime.datetime`

            Should be comparable with ``value`` attribute type.

            You can compare two ``DateTimeHWM`` or ``datetime`` values.

            But you cannot compare ``datetime`` with ``int`` value,
            as well as different HWM types, like ``DateTimeHWM`` and ``IntHWM``.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from datetime import datetime
            from etl_entities import DateTimeHWM

            hwm1 = DateTimeHWM(
                value=datetime(year=2021, month=12, day=30, hour=11, minute=22, second=33), ...
            )
            hwm2 = DateTimeHWM(
                value=datetime(year=2021, month=12, day=31, hour=1, minute=11, second=22), ...
            )

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, HWM):
            return isinstance(other, DateTimeHWM) and self.dict() == other.dict()

        return self.value == other

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.datetime_hwm.DateTimeHWM` or :obj:`datetime.datetime`

            Should be comparable with ``value`` attribute type.

            You can compare two ``DateTimeHWM`` or ``datetime`` values.

            But you cannot compare ``datetime`` with ``int`` value,
            as well as different HWM types, like ``DateTimeHWM`` and ``IntHWM``.

            .. warning::

                You cannot compare HWMs if one of them has ``None`` value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from datetime import datetime
            from etl_entities import DateTimeHWM

            hwm1 = DateTimeHWM(
                value=datetime(year=2021, month=12, day=30, hour=11, minute=22, second=33), ...
            )
            hwm2 = DateTimeHWM(
                value=datetime(year=2021, month=12, day=31, hour=00, minute=11, second=22), ...
            )

            assert hwm1 < hwm2
            assert hwm2 > hwm1

            assert hwm1 < datetime(year=2021, month=12, day=31, hour=1, minute=11, second=22)
            assert hwm1 > datetime(year=2021, month=12, day=30, hour=11, minute=22, second=33)

            hwm3 = DateTimeHWM(value=None, ...)
            assert hwm1 < hwm3  # will raise TypeError
            assert hwm1 < None  # same thing
        """

        if isinstance(other, HWM):
            if isinstance(other, DateTimeHWM):
                if self.dict(exclude={"value"}) == other.dict(exclude={"value"}):
                    return self.value < other

                raise NotImplementedError(  # NOSONAR
                    f"Cannot compare {self.__class__.__name__} with different column, table or process",
                )

            return NotImplemented

        return self.value < other