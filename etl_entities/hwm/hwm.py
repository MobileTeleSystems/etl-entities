# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Any, Generic, TypeVar

try:
    from pydantic.v1 import Field, validate_model
except (ImportError, AttributeError):
    from pydantic import Field, validate_model  # type: ignore[no-redef, assignment]

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
        --------

        >>> from etl_entities.hwm import ColumnIntHWM
        >>> hwm = ColumnIntHWM(value=1, name="my_hwm")
        >>> hwm = hwm.set_value(2)
        >>> hwm.value
        2
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
                raise ValueError(f"Type {type_name!r} does not match class {cls.__qualname__!r}")

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
