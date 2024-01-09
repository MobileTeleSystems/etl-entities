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

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import Field, validate_model

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry

ValueType = TypeVar("ValueType")
HWMType = TypeVar("HWMType", bound="HWM")


class HWM(ABC, Generic[ValueType], GenericModel):
    """Generic HWM type

    Parameters
    ----------
    column : ``str``

        Column name

    name : ``str``

        HWM unique name

    value : ``ColumnValueType`` or ``None``, default: ``None``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression, for example:  ``CAST(column as TYPE)``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time
    """

    name: str
    description: str = ""
    entity: Any = None
    value: ValueType  # it is important to keep order of entity and value as pydantic validation relies on it!
    expression: Any = None
    modified_time: datetime = Field(default_factory=datetime.now)

    class Config:  # noqa: WPS431
        extra = "forbid"

    def set_value(self: HWMType, value: ValueType | None) -> HWMType:
        """Replaces current HWM value with the passed one, and return HWM.

        .. note::

            Changes HWM value in place instead of returning new one

        Returns
        -------
        result : HWM

            Self

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm = ColumnIntHWM(value=1, ...)

            hwm.set_value(2)
            assert hwm.value == 2
        """

        new_value = self._check_new_value(value)

        if self.value != new_value:
            object.__setattr__(self, "value", new_value)  # noqa: WPS609
            object.__setattr__(self, "modified_time", datetime.now())  # noqa: WPS609

        return self

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

        result = super().serialize()
        result["type"] = HWMTypeRegistry.get_key(self.__class__)
        return result

    @classmethod
    def deserialize(cls: type[HWMType], inp: dict) -> HWMType:
        """Return HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        ----------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            assert ColumnIntHWM.deserialize(
                {
                    "value": "1",
                    "type": "int",
                    "column": "column_name",
                    "name": "name",
                }
            ) == ColumnIntHWM(value=1, ...)

            ColumnIntHWM.deserialize({"type": "date"})  # raises ValueError
        """

        value = deepcopy(inp)
        type_name = value.pop("type", None)
        if type_name:
            hwm_type = HWMTypeRegistry.get(type_name)
            if not issubclass(cls, hwm_type):
                raise ValueError(f"Type {type_name} does not match class {cls.__name__}")

        return super().deserialize(value)

    @abstractmethod
    def update(self: HWMType, value: Any) -> HWMType:
        """Update current HWM value with some implementation-specific logic, and return HWM"""

    def _check_new_value(self, value):
        validated_dict, _, validation_error = validate_model(
            self.__class__,
            self.copy(update={"value": value}).__dict__,
        )
        if validation_error:
            raise validation_error

        return validated_dict["value"]
