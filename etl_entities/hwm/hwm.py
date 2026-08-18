# SPDX-FileCopyrightText: 2023-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import sys
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import ConfigDict, Field

from etl_entities.entity import BaseModel
from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

ValueType = TypeVar("ValueType")
HWMType = TypeVar("HWMType", bound="HWM")


class HWM(BaseModel, Generic[ValueType]):
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

    model_config = ConfigDict(extra="forbid")

    def set_value(self, value: ValueType | None) -> Self:
        """Replaces current HWM value with the passed one, and return HWM.

        .. note::

            Changes HWM value in place instead of returning new one

        Returns
        -------
        result : HWM

            Self

        Examples
        --------

        >>> from etl_entities.hwm import ColumnIntHWM
        >>> hwm = ColumnIntHWM(value=1, name="my_hwm")
        >>> hwm = hwm.set_value(2)
        >>> hwm.value
        2
        """

        new_value = self._check_new_value(value)

        if self.value != new_value:
            object.__setattr__(self, "value", new_value)
            object.__setattr__(self, "modified_time", datetime.now())  # noqa: DTZ005

        return self

    def serialize(self) -> dict:
        """Return dict representation of HWM

        Returns
        -------
        result : dict

            Serialized HWM

        Examples
        --------

        >>> from etl_entities.hwm import ColumnIntHWM

        >>> hwm = ColumnIntHWM(name="my_hwm", value=1, entity="some_column", description="some description")
        >>> json = hwm.serialize()
        >>> json["type"]
        'column_int'
        >>> json["name"]
        'my_hwm'
        >>> json["value"]
        1
        >>> json["entity"]
        'some_column'
        >>> json["description"]
        'some description'
        """

        result = self.model_dump(mode="json", warnings=False)
        result["type"] = HWMTypeRegistry.get_key(self.__class__)
        return result

    @classmethod
    def deserialize(cls, inp: dict) -> Self:
        """Return HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        --------
        >>> from etl_entities.hwm import ColumnIntHWM
        >>> hwm = ColumnIntHWM.deserialize(
        ...     {
        ...         "type": "column_int",
        ...         "name": "my_hwm",
        ...         "value": "1",
        ...         "entity": "some_column",
        ...         "description": "some description",
        ...     }
        ... )
        >>> type(hwm)
        <class 'etl_entities.hwm.column.int_hwm.ColumnIntHWM'>
        >>> hwm.name
        'my_hwm'
        >>> hwm.value
        1
        >>> hwm.entity
        'some_column'
        >>> hwm.description
        'some description'
        >>> ColumnIntHWM.deserialize({"type": "column_date"})
        Traceback (most recent call last):
            ...
        ValueError: Type 'column_date' does not match class 'ColumnIntHWM'
        """

        value = deepcopy(inp)
        type_name = value.pop("type", None)
        if type_name:
            hwm_type = HWMTypeRegistry.get(type_name)
            if not issubclass(cls, hwm_type):
                msg = f"Type {type_name!r} does not match class {cls.__qualname__!r}"
                raise ValueError(msg)

        return cls.model_validate(value)

    @abstractmethod
    def update(self: HWMType, value: Any) -> HWMType:
        """Update current HWM value with some implementation-specific logic and return HWM"""

    @abstractmethod
    def reset(self: HWMType) -> HWMType:
        """Reset HWM value with some implementation-specific logic and return HWM"""

    def _check_new_value(self, value):
        new_dict = self.model_copy(update={"value": value}).model_dump(warnings=False)
        new_model = self.model_validate(new_dict, by_name=True)
        return new_model.value
