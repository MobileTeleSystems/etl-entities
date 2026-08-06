# SPDX-FileCopyrightText: 2023-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from pydantic import StrictInt, field_validator

from etl_entities.hwm.column.column_hwm import ColumnHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type


@register_hwm_type("column_int")
class ColumnIntHWM(ColumnHWM[int]):
    """HWM based on tracking latest column value of type :obj:`int`.

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

    value: StrictInt | None = None

    @field_validator("value", mode="before")
    @classmethod
    def _validate_value(cls, raw_value):
        if raw_value is None or raw_value == "null":
            return None

        if isinstance(raw_value, str):
            try:
                raw_value = Decimal(raw_value)
            except InvalidOperation:
                # pydantic will raise validation error
                return raw_value

        try:
            real_value = int(raw_value)
            if raw_value == real_value:
                return real_value
        except (ValueError, TypeError):
            pass

        # pydantic will raise validation error
        return raw_value
