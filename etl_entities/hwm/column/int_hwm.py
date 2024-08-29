# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

try:
    from pydantic.v1 import StrictInt, validator
except (ImportError, AttributeError):
    from pydantic import StrictInt, validator  # type: ignore[no-redef, assignment]

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_int")
class ColumnIntHWM(ColumnHWM[int]):
    """Integer HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``int`` or ``None``, default: ``None``

        HWM value

    description :  ``str``, default: ``""``

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

        from etl_entities.hwm import ColumnIntHWM

        hwm_int = ColumnIntHWM(
            name="long_unique_name",
            source="myschema.mytable",
            expression="my_int_column",
            value=1,
        )
    """

    value: Optional[StrictInt] = None

    @validator("value", pre=True)
    def _validate_value(cls, raw_value):  # noqa: N805
        if raw_value is None or raw_value == "null":
            return None

        if isinstance(raw_value, str):
            try:
                raw_value = Decimal(raw_value)
            except InvalidOperation:
                # pydantic will raise validation error
                return raw_value

        real_value = int(raw_value)
        if raw_value == real_value:
            return real_value

        # pydantic will raise validation error
        return raw_value
