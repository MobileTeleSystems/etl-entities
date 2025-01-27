# SPDX-FileCopyrightText: 2021-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Mapping

from frozendict import frozendict

try:
    from pydantic.v1 import validator
except (ImportError, AttributeError):
    from pydantic import validator  # type: ignore[no-redef, assignment]

from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.hwm.key_value.key_value_hwm import KeyValueHWM


@register_hwm_type("key_value_int")
class KeyValueIntHWM(KeyValueHWM[int, int]):
    """HWM type storing ``int -> int`` mapping.

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``frozendict[int, int]``, default: ``frozendict``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    entity : Any, default: ``None``

        HWM entity, e.g. topic name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``offset``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    --------

    .. code:: python

        from etl_entities.hwm import KeyValueIntHWM

        hwm_kv_int = KeyValueIntHWM(
            name="long_unique_name",
            source="topic_name",
            expression="offset",
            value={
                0: 100,  # 0 and 1 - partition numbers
                1: 123,  # 100 and 123 - offset values
            },
        )
    """

    def serialize(self) -> dict:
        # Convert self.value to a regular dictionary if it is a frozendict
        # This is necessary because frozendict objects are not natively serializable to JSON.
        serialized_data = {
            "name": self.name,
            "value": dict(self.value),
            "description": self.description,
            "entity": self.entity,
            "expression": self.expression,
            "modified_time": self.modified_time.isoformat() if self.modified_time else None,
            "type": "key_value_int",
        }
        return serialized_data  # noqa: WPS331

    @validator("value", pre=True)
    def _validate_int_values(cls, key_value):  # noqa: N805
        if isinstance(key_value, Mapping):
            result = {}
            for key, value in key_value.items():
                if not isinstance(key, (int, str)):
                    raise TypeError(f"key should be integer, got {key!r}")
                if not isinstance(value, (int, str)):
                    raise TypeError(f"Value should be integer, got {value!r}")
                result[int(key)] = int(value)
            return frozendict(result)

        return key_value
