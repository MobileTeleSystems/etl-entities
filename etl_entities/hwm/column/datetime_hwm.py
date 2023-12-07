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

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_datetime")
class ColumnDateTimeHWM(ColumnHWM[datetime]):
    """DateTime HWM type


    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : :obj:`datetime.datetime` or ``None``, default: ``None``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    source : Any, default: ``None``

        HWM source, e.g. table name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``column``, ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    ----------

    .. code:: python

        from datetime import datetime
        from etl_entities.hwm import ColumnDateTimeHWM

        hwm = DateTimeHWM(
            name="long_unique_name",
            source="myschema.mytable",
            expression="my_timestamp_column",
            value=datetime(year=2021, month=12, day=31, hour=11, minute=22, second=33),
        )
    """

    value: Optional[datetime] = None

    @validator("value", pre=True)
    def _validate_value(cls, value):  # noqa: N805
        # we need to deserialize values, as pydantic parses fields in unexpected way:
        # https://docs.pydantic.dev/latest/api/standard_library_types/#datetimedatetime
        if isinstance(value, int):
            raise ValueError("Cannot convert integer to datetime")

        if isinstance(value, str):
            result = strict_str_validator(value).strip()
            if result.lower() == "null":
                return None

            return datetime.fromisoformat(result)

        return value
