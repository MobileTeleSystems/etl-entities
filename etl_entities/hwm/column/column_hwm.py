# SPDX-FileCopyrightText: 2023-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from typing import Generic, TypeVar

from pydantic import Field
from typing_extensions import Self

from etl_entities.hwm.hwm import HWM

ColumnValueType = TypeVar("ColumnValueType")
ColumnHWMType = TypeVar("ColumnHWMType", bound="ColumnHWM")


class ColumnHWM(HWM[ColumnValueType | None], Generic[ColumnValueType]):  # noqa: PLW1641
    """Base column HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``ColumnValueType`` or ``None``, default: ``None``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    source : Any, default: ``None``

        HWM source, e.g. table name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``column``, ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time
    """

    entity: str | None = Field(default=None, alias="source")
    value: ColumnValueType | None = None

    def __add__(self, value: ColumnValueType) -> Self:
        """Increase HWM value and return copy of HWM

        Parameters
        ----------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot add ``str`` to ``int`` value, but you can add ``int`` to ``int``.

        Returns
        -------
        result : ColumnHWM

            HWM with new value

        Examples
        --------

        >>> hwm = ColumnHWM(value=100, name="my_hwm")
        >>> hwm = hwm + 2
        >>> hwm.value
        102
        """

        new_value = self.value + value  # type: ignore[operator]
        if self.value != new_value:
            return self.model_copy().set_value(new_value)

        return self

    def __sub__(self, value: ColumnValueType) -> Self:
        """Decrease HWM value, and return copy of HWM

        Parameters
        ----------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot subtract ``str`` from ``int`` value, but you can subtract ``int`` from ``int``.

        Returns
        -------
        result : ColumnHWM

            HWM copy with new value

        Examples
        --------

        >>> hwm = ColumnHWM(value=100, name="my_hwm")
        >>> hwm = hwm - 2
        >>> hwm.value
        98
        """

        new_value = self.value - value  # type: ignore[operator]
        if self.value != new_value:
            return self.model_copy().set_value(new_value)

        return self

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Parameters
        ----------
        other : :obj:`etl_entities.hwm.column_hwm.ColumnHWM`

            You can compare two :obj:`etl_entities.hwm.column_hwm.ColumnHWM` instances,
            obj:`etl_entities.hwm.column_hwm.ColumnHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

        Returns
        -------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        self_fields = self.model_dump(exclude={"modified_time"}, warnings=False)
        other_fields = other.model_dump(exclude={"modified_time"}, warnings=False)
        return self_fields == other_fields

    def update(self, value: ColumnValueType) -> Self:
        """Updates current HWM value with some implementation-specific logic, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : ColumnHWM

            HWM copy with new value

        Examples
        --------

        >>> from etl_entities.hwm import ColumnIntHWM
        >>> hwm = ColumnIntHWM(value=1, name="my_hwm")
        >>> hwm = hwm.update(2)
        >>> hwm.value
        2
        >>> hwm = hwm.update(1)
        >>> hwm.value  # value cannot decrease
        2
        """

        if self.value is None or self.value < value:  # type: ignore[operator]
            return self.set_value(value)

        return self

    def reset(self) -> Self:
        """Reset current HWM value and return HWM.

        .. note::

            Changes HWM value in-place

        Returns
        -------
        result : ColumnHWM

            Self

        Examples
        --------

        >>> from etl_entities.hwm import ColumnIntHWM
        >>> hwm = ColumnIntHWM(value=1, name="my_hwm")
        >>> hwm = hwm.reset()
        >>> hwm.value
        """
        return self.set_value(None)

    def __lt__(self, other):
        """Checks current HWM value is less than another one.

        Returns
        -------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Raises
        ------
        NotImplementedError:

            If someone tries to compare HWMs with different fields,
            like :obj:`name`, :obj:`source` or :obj:`expression`
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        self_fields = self.model_dump(exclude={"value", "modified_time"}, warnings=False)
        other_fields = other.model_dump(exclude={"value", "modified_time"}, warnings=False)
        if self_fields != other_fields:
            msg = "Cannot compare ColumnHWM with different entity or expression"
            raise NotImplementedError(
                msg,
            )

        return self.value < other.value
