from __future__ import annotations

from functools import total_ordering
from typing import Optional

from etl_entities.hwm.column_hwm import ColumnHWM
from etl_entities.hwm.hwm import HWM


@total_ordering
class IntHWM(ColumnHWM[int]):
    """Integer HWM type

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

    value: Optional[int] = None

    def serialize(self) -> str:  # noqa: WPS612
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm = IntHWM(value=1, ...)
            assert hwm.serialize() == "1"

            hwm = IntHWM(value=None, ...)
            assert hwm.serialize() == "null"
        """

        return super().serialize()

    @classmethod
    def deserialize(cls, value: str) -> int | None:
        """Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`int` or ``None``

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            assert IntHWM.deserialize("123") == 123

            assert IntHWM.deserialize("null") is None
        """

        value = super().deserialize(value)

        if value.lower() == "null":
            return None

        return int(value)

    def with_value(self, value: int | None) -> ColumnHWM:
        """Create copy of HWM object with specified value

        Parameters
        ----------
        value : Any

            New HWM value

        Returns
        -------
        result : HWM

            Copy of HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm = IntHWM(value=1, ...)
            new_hwm = hwm.with_value(2)

            assert new_hwm.value == 2
        """

        if value is not None:
            dct = self.dict()
            dct["value"] = int(value)
            return self.parse_obj(dct)

        return self

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : ``IntHWM`` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types, like ``IntHWM`` and ``DateHWM``.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm1 = IntHWM(value=1, ...)
            hwm2 = IntHWM(value=2, ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, HWM):
            return isinstance(other, IntHWM) and self.dict() == other.dict()

        return self.value == other

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : ``IntHWM`` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types, like ``IntHWM`` and ``DateHWM``.

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm1 = IntHWM(value=1, ...)
            hwm2 = IntHWM(value=2, ...)

            assert hwm1 < hwm2
            assert hwm1 > hwm2

            assert hwm1 < 2
            assert hwm1 > 0

            hwm3 = IntHWM(value=None, ...)
            assert hwm1 < hwm3  # will raise TypeError
            assert hwm1 < None  # same thing
        """

        if isinstance(other, HWM):
            if isinstance(other, IntHWM):
                if self.dict(exclude={"value"}) == other.dict(exclude={"value"}):
                    return self.value < other.value

                raise NotImplementedError(  # NOSONAR
                    f"Cannot compare {self.__class__.__name__} with different column, table or process",
                )

            return NotImplemented

        return self.value < other
