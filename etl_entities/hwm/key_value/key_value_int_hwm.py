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

from frozendict import frozendict
from pydantic import Field, validator

from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.hwm.key_value.key_value_hwm import KeyValueHWM


@register_hwm_type("key_value_int")
class KeyValueIntHWM(KeyValueHWM[int]):
    """Integer KeyValue HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``frozendict[Any, KeyValueHWMValueType]``, default: ``frozendict``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    source : Any, default: ``None``

        HWM source, e.g. topic name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``offset``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    ----------

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

    # employing frozendict without specifying `frozendict[Any, int]`
    # due to the lack of support for generic dict annotations in Python 3.7.
    value: frozendict = Field(default_factory=frozendict)

    def serialize(self) -> dict:
        """Return dict representation of HWM

        Returns
        -------
        result : dict

            Serialized HWM

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm = ColumnIntHWM(value=1, ...)
            assert hwm.serialize() == {
                "value": "1",
                "type": "int",
                "column": "column_name",
                "name": "table_name",
                "description": ...,
            }
        """

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
        if key_value is None:
            return key_value
        new_key_value = {}
        for key, value in key_value.items():
            if not isinstance(value, (int, str)):
                raise ValueError
            else:
                new_key_value[key] = int(value)

        return frozendict(new_key_value)
