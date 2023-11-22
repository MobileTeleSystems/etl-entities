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

from typing import Any, Generic, Optional, TypeVar

from pydantic import Field

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM

ColumnValueType = TypeVar("ColumnValueType")


class ColumnHWM(HWM[Optional[ColumnValueType]], Generic[ColumnValueType], GenericModel):
    """Base column HWM type

    Parameters
    ----------
    column : ``str``

        Column name

    name : ``str``

        Table name

    value : ``ColumnValueType`` or ``None``, default: ``None``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression, for example:  ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time
    """

    entity: str = Field(alias="column")
    name: str
    value: Optional[ColumnValueType] = None
    description: str = ""
    expression: Any = None

    def covers(self, value: Optional[ColumnValueType]) -> bool:
        """Return ``True`` if input value is already covered by HWM

        Examples
        ----------

        .. code:: python

            hwm = ColumnHWM(column="column_name", value=1)

            assert hwm.covers(0)  # 0 <= 1
            assert hwm.covers(1)  # 1 <= 1
            assert hwm.covers(0.5)  # 0.5 <= 1
            assert not hwm.covers(2)  # 2 > 1

            empty_hwm = ColumnHWM(column="column_name")

            assert not empty_hwm.covers(0)  # non comparable with None
            assert not empty_hwm.covers(1)  # non comparable with None
            assert not empty_hwm.covers(0.5)  # non comparable with None
            assert not empty_hwm.covers(2)  # non comparable with None
        """

        if self.value is None:
            return False

        return self._check_new_value(value) <= self.value

    def __add__(self, value):
        """Increase HWM value and return copy of HWM

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot add ``str`` to ``int`` value, but you can add ``int`` to ``int``.

        Returns
        --------
        result : ColumnHWM

            HWM with new value

        Examples
        ----------

        .. code:: python

            # assume val2 == val1 + inc

            hwm1 = ColumnHWM(value=val1, ...)
            hwm2 = ColumnHWM(value=val2, ...)

            # same as ColumnHWM(value=hwm1.value + inc, ...)
            assert hwm1 + inc == hwm2
        """

        new_value = self.value + value
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __sub__(self, value):
        """Decrease HWM value, and return copy of HWM

        Params
        -------
        value : ``Any`` or ``None``

            Should be compatible with ``value`` attribute type.

            For example, you cannot subtract ``str`` from ``int`` value, but you can subtract ``int`` from ``int``.

        Returns
        --------
        result : ColumnHWM

            HWM copy with new value

        Examples
        ----------

        .. code:: python

            # assume val2 == val1 - dec

            hwm1 = ColumnHWM(value=val1, ...)
            hwm2 = ColumnHWM(value=val2, ...)

            # same as ColumnHWM(value=hwm1.value - dec, ...)
            assert hwm1 - dec == hwm2
        """

        new_value = self.value - value
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.column_hwm.ColumnHWM` or any :obj:`object`

            You can compare two :obj:`hwmlib.hwm.column_hwm.ColumnHWM` instances,
            obj:`hwmlib.hwm.column_hwm.ColumnHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.
        """

        if isinstance(other, HWM):
            self_fields = self.dict(exclude={"modified_time"})
            other_fields = other.dict(exclude={"modified_time"})
            return isinstance(other, ColumnHWM) and self_fields == other_fields

        return self.value == other

    def update(self, value: ColumnValueType):
        """Updates current HWM value with some implementation-specific logic, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : ColumnHWM

            HWM copy with new value

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm = ColumnIntHWM(value=1, ...)

            hwm.update(2)
            assert hwm.value == 2

            hwm.update(1)
            assert hwm.value == 2  # value cannot decrease
        """

        if self.value is None:
            return self.set_value(value)

        if self.value < value:  # type: ignore[operator]
            return self.set_value(value)

        return self

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.column_hwm.ColumnHWM` or any :obj:`object`

            You can compare two :obj:`hwmlib.hwm.column_hwm.ColumnHWM` instances,
            obj:`hwmlib.hwm.column_hwm.ColumnHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.
        """

        if isinstance(other, HWM):
            if isinstance(other, ColumnHWM):
                self_fields = self.dict(exclude={"value", "modified_time"})
                other_fields = other.dict(exclude={"value", "modified_time"})
                if self_fields == other_fields:
                    return self.value < other.value

                raise NotImplementedError(  # NOSONAR
                    "Cannot compare ColumnHWM with different column, source or process",
                )

            return NotImplemented

        return self.value < other
