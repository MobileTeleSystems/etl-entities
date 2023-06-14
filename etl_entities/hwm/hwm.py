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

import json
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import Field, validate_model

from etl_entities.entity import Entity, GenericModel
from etl_entities.process import Process, ProcessStackManager

ValueType = TypeVar("ValueType")
SerializedType = TypeVar("SerializedType")


class HWM(ABC, Entity, GenericModel, Generic[ValueType, SerializedType]):
    """Generic HWM type

    Parameters
    ----------
    value : Any

        HWM value of any type

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance
    """

    source: Entity
    value: ValueType
    modified_time: datetime = Field(default_factory=datetime.now)
    process: Process = Field(default_factory=ProcessStackManager.get_current)

    def set_value(self, value: ValueType) -> HWM:
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

            from etl_entities import IntHWM

            hwm = IntHWM(value=1, ...)

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

            from etl_entities import IntHWM

            hwm = IntHWM(value=1, ...)
            assert hwm.serialize() == {
                "value": "1",
                "type": "int",
                "column": {"name": ..., "partition": ...},
                "source": ...,
                "process": ...,
            }
        """

        # small hack to avoid circular imports
        from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry

        result = json.loads(self.json())
        result["value"] = self.serialize_value()
        result["type"] = HWMTypeRegistry.get_key(self.__class__)
        return result

    @classmethod
    def deserialize(cls, inp: dict):
        """Return HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            assert IntHWM.deserialize(
                {
                    "value": "1",
                    "type": "int",
                    "column": {"name": ..., "partition": ...},
                    "source": ...,
                    "process": ...,
                }
            ) == IntHWM(value=1, ...)

            IntHWM.deserialize({"type": "date"})  # raises ValueError
        """

        # small hack to avoid circular imports
        from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry

        value = deepcopy(inp)
        typ = value.pop("type", None)
        if typ:
            hwm_type = HWMTypeRegistry.get(typ)
            if not issubclass(cls, hwm_type):
                raise ValueError(f"Type {typ} does not match class {cls.__name__}")

        return super().deserialize(value)

    @abstractmethod
    def serialize_value(self) -> SerializedType:
        """Return string representation of HWM value

        Returns
        -------
        result : json

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import HWM

            hwm = HWM(value=1, ...)
            assert hwm.serialize_value() == "1"
        """

    @abstractmethod
    def covers(self, value) -> bool:
        """Return ``True`` if input value is already covered by HWM"""

    @abstractmethod
    def update(self, value):
        """Update current HWM value with some implementation-specific logic, and return HWM"""

    def _check_new_value(self, value):
        validated_dict, _, validation_error = validate_model(
            self.__class__,
            self.copy(update={"value": value}).__dict__,
        )
        if validation_error:
            raise validation_error

        return validated_dict["value"]
