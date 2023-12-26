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
from pydantic import Field

from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.hwm.key_value.key_value_hwm import KeyValueHWM


@register_hwm_type("key_value_int")
class KeyValueIntHWM(KeyValueHWM[int]):
    """Integer KeyValue HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``frozendict[Any, KeyValueHWMValueType]]]``, default: ``frozendict``

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

    value: frozendict = Field(default_factory=frozendict)
