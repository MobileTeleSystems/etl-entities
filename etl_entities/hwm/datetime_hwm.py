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

from datetime import datetime
from typing import Optional

from pydantic import validator
from pydantic.validators import strict_str_validator

from etl_entities.hwm.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("datetime")
class DateTimeHWM(ColumnHWM[datetime]):
    """DateTime HWM type

    Parameters
    ----------
    column : :obj:`etl_entities.source.db.column.Column`

        Column instance

    source : :obj:`etl_entities.source.db.table.Table`

        Table instance

    value : :obj:`datetime.datetime` or ``None``, default: ``None``

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from datetime import datetime
        from etl_entities import DateTimeHWM, Column, Table

        column = Column(name="id")
        table = Table(name="mydb.mytable", instance="postgres://db.host:5432")

        hwm = DateTimeHWM(
            column=column,
            source=table,
            value=datetime(year=2021, month=12, day=31, hour=11, minute=22, second=33),
        )
    """

    value: Optional[datetime] = None

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

            from datetime import datetime
            from etl_entities import DateTimeHWM

            hwm = DateTimeHWM(
                value=datetime(year=2021, month=12, day=31, hour=11, minute=22, second=33), ...
            )
            assert hwm.serialize_value() == "2021-12-31T11:22:33"

            hwm = DateTimeHWM(value=None, ...)
            assert hwm.serialize_value() == "null"
        """

        if self.value is None:
            return "null"

        return self.value.isoformat()

    @classmethod
    def deserialize_value(cls, value: str) -> datetime | None:
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

            assert DateTimeHWM.deserialize_value("2021-12-31T11-22-33") == datetime(
                year=2021, month=12, day=31, hour=11, minute=22, second=33
            )

            assert DateTimeHWM.deserialize_value("null") is None
        """

        result = strict_str_validator(value).strip()

        if result.lower() == "null":
            return None
        return datetime.fromisoformat(result)

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.datetime_hwm.DateTimeHWM` or :obj:`datetime.datetime`

            Should be comparable with ``value`` attribute type.

            You can compare two :obj:`hwmlib.hwm.datetime_hwm.DateTimeHWM` or ``datetime`` values.

            But you cannot compare ``datetime`` with ``int`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.datetime_hwm.DateTimeHWM` and :obj:`hwmlib.hwm.int_hwm.IntHWM`.

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

        if isinstance(other, ColumnHWM) and not isinstance(other, DateTimeHWM):
            return False

        return super().__eq__(other)

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.datetime_hwm.DateTimeHWM` or :obj:`datetime.datetime`

            Should be comparable with ``value`` attribute type.

            You can compare two :obj:`hwmlib.hwm.datetime_hwm.DateTimeHWM` or ``datetime`` values.

            But you cannot compare ``datetime`` with ``int`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.datetime_hwm.DateTimeHWM` and :obj:`hwmlib.hwm.int_hwm.IntHWM`.

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

        if isinstance(other, ColumnHWM) and not isinstance(other, DateTimeHWM):
            return NotImplemented

        return super().__lt__(other)
