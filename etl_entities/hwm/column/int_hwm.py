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

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_int")
class ColumnIntHWM(ColumnHWM[int]):
    """Integer HWM type

    Parameters
    ----------
    column : ``str``

        Column name

    name : ``str``

        Table name

    value : ``int`` or ``None``, default: ``None``

        HWM value

    description :  ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression, for example:  ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    ----------

    .. code:: python

        from etl_entities.hwm import ColumnIntHWM

        hwm_int = ColumnIntHWM(column="column_name", value=1, name="table_name")
    """

    value: Optional[int] = None

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Params
        -------
        other : :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM` and :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM`.

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm1 = ColumnIntHWM(value=1, ...)
            hwm2 = ColumnIntHWM(value=2, ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if isinstance(other, ColumnHWM) and not isinstance(other, ColumnIntHWM):
            return False

        return super().__eq__(other)

    def __lt__(self, other):
        """Checks current ColumnIntHWM value is less than another one

        Params
        -------
        other : :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM` or :obj:`int`

            Should be comparable with ``value`` attribute type.

            You can compare two ``int`` values, but you cannot compare ``int`` with ``date`` value,
            as well as different HWM types,
            like :obj:`hwmlib.hwm.int_hwm.ColumnIntHWM` and :obj:`hwmlib.hwm.date_hwm.ColumnDateHWM`.

            .. warning::

                You cannot compare HWMs if one of them has None value

        Returns
        --------
        result : bool

            ``True`` if current HWM value is less than provided value, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm1 = ColumnIntHWM(value=1, ...)
            hwm2 = ColumnIntHWM(value=2, ...)

            assert hwm1 < hwm2
            assert hwm1 > hwm2

            assert hwm1 < 2
            assert hwm1 > 0

            hwm3 = ColumnIntHWM(value=None, ...)
            assert hwm1 < hwm3  # will raise TypeError
            assert hwm1 < None  # same thing
        """

        if isinstance(other, ColumnHWM) and not isinstance(other, ColumnIntHWM):
            return NotImplemented

        return super().__lt__(other)
