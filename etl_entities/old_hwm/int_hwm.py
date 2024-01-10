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

from typing import Optional

import typing_extensions
from pydantic import validator
from pydantic.types import StrictInt
from pydantic.validators import int_validator

from etl_entities.hwm import ColumnIntHWM, register_hwm_type
from etl_entities.old_hwm.column_hwm import ColumnHWM


@typing_extensions.deprecated(
    "Deprecated in v2.0, will be removed in v3.0",
    category=UserWarning,
)
@register_hwm_type("old_column_int")
class IntHWM(ColumnHWM[StrictInt]):
    """Integer HWM type

    .. deprecated:: 2.0.0
        Use :obj:`ColumnIntHWM <etl_entities.hwm.column.int_hwm.ColumnIntHWM>` instead

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    source : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : int or ``None``, default: ``None``

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from etl_entities.old_hwm import IntHWM
        from etl_entities.source import Column, Table

        column = Column(name="id")
        table = Table(name="mydb.mytable", instance="postgres://db.host:5432")

        old_hwm = IntHWM(column=column, source=table, value=1)
    """

    value: Optional[StrictInt] = None

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, str):
            return cls.deserialize_value(value)

        return value

    def serialize_value(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities.old_hwm import DateHWM

            old_hwm = DateHWM(value=date(year=2021, month=12, day=31), ...)
            assert old_hwm.serialize_value() == "2021-12-31"

            old_hwm = DateHWM(value=None, ...)
            assert old_hwm.serialize_value() == "null"
        """

        if self.value is None:
            return "null"

        return str(self.value)

    def as_new_hwm(self):
        return ColumnIntHWM(
            name=self.qualified_name,
            source=self.source.name,
            expression=self.column.name,
            value=self.value,
            modified_time=self.modified_time,
        )

    @classmethod
    def deserialize_value(cls, value: str) -> int | None:
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

            from etl_entities.old_hwm import IntHWM

            assert IntHWM.deserialize_value("123") == 123

            assert IntHWM.deserialize_value("null") is None
        """

        if str(value).lower() == "null":
            return None

        return int_validator(value)

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.old_hwm.int_hwm.IntHWM` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types,
            like :obj:`etl_entities.old_hwm.int_hwm.IntHWM` and :obj:`etl_entities.old_hwm.date_hwm.DateHWM`.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities.old_hwm import IntHWM

            hwm1 = IntHWM(value=1, ...)
            hwm2 = IntHWM(value=2, ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, ColumnHWM) and not isinstance(other, IntHWM):
            return False

        return super().__eq__(other)

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.old_hwm.int_hwm.IntHWM` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types,
            like :obj:`etl_entities.old_hwm.int_hwm.IntHWM` and :obj:`etl_entities.old_hwm.date_hwm.DateHWM`.

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities.old_hwm import IntHWM

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

        if isinstance(other, ColumnHWM) and not isinstance(other, IntHWM):
            return NotImplemented

        return super().__lt__(other)
