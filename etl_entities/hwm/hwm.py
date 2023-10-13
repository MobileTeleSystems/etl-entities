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
from typing import Any, Generic, Optional, TypeVar

from pydantic import Field, validate_model

from etl_entities.entity import GenericModel
from etl_entities.hwm_utils import HWMTypeRegistry

ValueType = TypeVar("ValueType")


class HWM(ABC, Generic[ValueType], GenericModel):
    """Generic HWM type

    Parameters
    ----------
    column : ``str``

        Column name

    name : ``str``

        Table name

    value : ``ColumnValueType`` or ``None``, default: ``None``

        HWM value

    description: ``str``, default: ``""``

        Description of HWM

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time
    """

    name: str
    value: Optional[ValueType]
    description: str = ""
    entity: Any = None
    expression: Any = None
    modified_time: datetime = Field(default_factory=datetime.now)

    def set_value(self, value: ValueType | None) -> HWM:
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

            from etl_entities import ColumnIntHWM

            hwm = ColumnIntHWM(value=1, ...)

            hwm.set_value(2)
            assert hwm.value == 2
        """

        new_value = self._check_new_value(value)

        if self.value != new_value:
            object.__setattr__(self, "value", new_value)  # noqa: WPS609
            object.__setattr__(self, "modified_time", datetime.now())  # noqa: WPS609

        return self

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
        typ = value.pop("type", None)
        if typ:
            hwm_type = HWMTypeRegistry.get(typ)
            if not issubclass(cls, hwm_type):
                raise ValueError(f"Type {typ} does not match class {cls.__name__}")

        return super().deserialize(value)

    @abstractmethod
    def covers(self, value: ValueType) -> bool:
        """Return ``True`` if input value is already covered by HWM"""

    def _check_new_value(self, value):
        validated_dict, _, validation_error = validate_model(
            self.__class__,
            self.copy(update={"value": value}).__dict__,
        )
        if validation_error:
            raise validation_error

        return validated_dict["value"]
