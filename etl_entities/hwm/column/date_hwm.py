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

from datetime import date
from typing import Optional

from pydantic import validator
from pydantic.validators import strict_str_validator

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_date")
class ColumnDateHWM(ColumnHWM[date]):
    """Date HWM type

    Parameters
    ----------
    column : ``str``

        Column name

    name : ``str``

        Table name

    value : :obj:`datetime.date` or ``None``, default: ``None``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression, for example:  ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    ----------

    .. code:: python

        from datetime import date
        from etl_entities.hwm import ColumnDateHWM

        hwm = ColumnDateHWM(
            column="column_name", value=date(year=2021, month=12, day=3), name="table_name"
        )
    """

    value: Optional[date] = None

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, str):
            return cls._deserialize_value(value)
        # we need to deserialize values, as pydantic parses fields in unexpected way:
        # https://docs.pydantic.dev/latest/api/standard_library_types/#datetimedatetime
        return value

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`etl_entities.hwm.date_hwm.ColumnDateHWM` or :obj:`datetime.date`

            Should be comparable with ``value`` attribute type.

            You can compare two :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM` or ``date`` values.

            But you cannot compare ``date`` with ``int`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM` and :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM`.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from datetime import date
            from etl_entities.hwm import ColumnDateHWM

            hwm1 = ColumnDateHWM(value=date(year=2021, month=12, day=30), ...)
            hwm2 = ColumnDateHWM(value=date(year=2021, month=12, day=31), ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, ColumnHWM) and not isinstance(other, ColumnDateHWM):
            return False

        return super().__eq__(other)

    def __lt__(self, other):
        """Checks current HWM value is less than another one

        Params
        -------
        other : :obj:`etl_entities.hwm.date_hwm.ColumnDateHWM` or :obj:`datetime.date`

            Should be comparable with ``value`` attribute type.

            You can compare two :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM` or ``date`` values.

            But you cannot compare ``date`` with ``int`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM` and :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM`.

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
            from etl_entities.hwm import ColumnDateHWM

            hwm1 = DateHWM(value=date(year=2021, month=12, day=30), ...)
            hwm2 = DateHWM(value=date(year=2021, month=12, day=31), ...)

            assert hwm1 < hwm2
            assert hwm2 > hwm1

            assert hwm1 < date(year=2021, month=12, day=1)
            assert hwm1 > date(year=2021, month=12, day=31)

            hwm3 = ColumnDateHWM(value=None, ...)
            assert hwm1 < hwm3  # will raise TypeError
            assert hwm1 < None  # same thing
        """

        if isinstance(other, ColumnHWM) and not isinstance(other, ColumnDateHWM):
            return NotImplemented

        return super().__lt__(other)

    @classmethod
    def _deserialize_value(cls, value: str) -> date | None:
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

            from etl_entities.hwm import ColumnDateHWM

            assert ColumnDateHWM.deserialize_value("2021-12-31") == date(
                year=2021, month=12, day=31
            )
            assert ColumnDateHWM.deserialize_value("null") is None
        """

        result = strict_str_validator(value).strip()

        if result.lower() == "null":
            return None
        return date.fromisoformat(result)
