from __future__ import annotations

from datetime import date
from functools import total_ordering
from typing import Optional

from etl_entities.hwm.column_hwm import ColumnHWM
from etl_entities.hwm.hwm import HWM


@total_ordering
class DateHWM(ColumnHWM[date]):
    """Date HWM type

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    table : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : :obj:`datetime.date` or ``None``, default: ``None``

        HWM value

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from datetime import date
        from etl_entities import DateHWM, Column, Table

        column = Column(name="id")
        table = Table(name="mytable", db="mydb", location="postgres://db.host:5432")

        hwm = DateHWM(column=column, table=table, value=date(year=2021, month=21, day=3))
    """

    value: Optional[date] = None

    def serialize(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import DateHWM

            hwm = DateHWM(value=date(year=2021, month=12, day=31), ...)
            assert hwm.serialize() == "2021-12-31"

            hwm = DateHWM(value=None, ...)
            assert hwm.serialize() == "null"
        """

        if self.value is None:
            return "null"

        return self.value.isoformat()

    @classmethod
    def deserialize(cls, value: str) -> date | None:
        """Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`datetime.date` or ``None``

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import DateHWM

            assert DateHWM.deserialize("2021-12-31") == date(year=2021, month=12, day=31)
            assert DateHWM.deserialize("null") is None
        """

        value = super().deserialize(value)

        if value.lower() == "null":
            return None

        return date.fromisoformat(value)

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.date_hwm.DateHWM` or :obj:`datetime.date`

            Should be comparable with ``value`` attribute type.

            You can compare two ``DateHWM`` or ``date`` values.

            But you cannot compare ``date`` with ``int`` value,
            as well as different HWM types, like ``DateHWM`` and ``IntHWM``.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from datetime import date
            from etl_entities import DateHWM

            hwm1 = DateHWM(value=date(year=2021, month=12, day=30), ...)
            hwm2 = DateHWM(value=date(year=2021, month=12, day=31), ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, HWM):
            return isinstance(other, DateHWM) and self.dict() == other.dict()

        return self.value == other

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.date_hwm.DateHWM` or :obj:`datetime.date`

            Should be comparable with ``value`` attribute type.

            You can compare two ``DateHWM`` or ``date`` values.

            But you cannot compare ``date`` with ``int`` value,
            as well as different HWM types, like ``DateHWM`` and ``IntHWM``.

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from datetime import date
            from etl_entities import DateHWM

            hwm1 = DateHWM(value=date(year=2021, month=12, day=30), ...)
            hwm2 = DateHWM(value=date(year=2021, month=12, day=31), ...)

            assert hwm1 < hwm2
            assert hwm2 > hwm1

            assert hwm1 < date(year=2021, month=12, day=1)
            assert hwm1 > date(year=2021, month=12, day=31)

            hwm3 = DateHWM(value=None, ...)
            assert hwm1 < hwm3  # will raise TypeError
            assert hwm1 < None  # same thing
        """

        if isinstance(other, HWM):
            if isinstance(other, DateHWM):
                if self.dict(exclude={"value"}) == other.dict(exclude={"value"}):
                    return self.value < other

                raise NotImplementedError(  # NOSONAR
                    f"Cannot compare {self.__class__.__name__} with different column, table or process",
                )

            return NotImplemented

        return self.value < other
