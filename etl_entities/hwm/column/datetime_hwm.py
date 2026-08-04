# SPDX-FileCopyrightText: 2023-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime

from pydantic import field_validator
from pydantic_core import PydanticCustomError

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_datetime")
class ColumnDateTimeHWM(ColumnHWM[datetime]):
    """HWM based on tracking latest column value of type :obj:`datetime.datetime`.

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
    --------

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

    value: datetime | None = None

    @field_validator("value", mode="before")
    @classmethod
    def _validate_value(cls, value):
        # we need to deserialize values, as pydantic parses fields in unexpected way:
        # https://docs.pydantic.dev/latest/api/standard_library_types/#datetimedatetime
        if isinstance(value, int):
            raise PydanticCustomError("datetime_parsing", "Cannot convert integer to datetime", {"value": value})  # noqa: EM101

        if isinstance(value, str):
            if value.lower() == "null":
                return None
            return datetime.fromisoformat(value)

        return value
