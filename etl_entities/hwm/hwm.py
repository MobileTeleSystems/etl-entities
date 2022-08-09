from __future__ import annotations

import json
from abc import abstractmethod
from copy import deepcopy
from datetime import datetime
from typing import Generic, TypeVar, cast

from pydantic import Field, validator
from pydantic.validators import strict_str_validator

from etl_entities.entity import Entity, GenericModel
from etl_entities.process import Process, ProcessStackManager

ValueType = TypeVar("ValueType")


class HWM(Entity, GenericModel, Generic[ValueType]):
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

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, str):
            return cls.deserialize_value(value)

        return value

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

        new_value = self.validate_value(value)
        # `validate_value` checks for specific types. if value of the unknown type is passed, it is returned as is
        # so a small hack here to force check if value is consistent with a type hint
        new_obj = self.__class__.parse_obj(self.copy(update={"value": new_value}))

        if self.value != new_obj.value:
            object.__setattr__(self, "value", new_obj.value)  # noqa: WPS609
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

    def serialize_value(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import HWM

            hwm = HWM(value=1, ...)
            assert hwm.serialize_value() == "1"
        """

        return str(self.value).strip()

    @classmethod
    def deserialize_value(cls, value: str) -> ValueType:
        """Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : ``Any``

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            assert IntHWM.deserialize_value("123") == 123
        """

        return cast(ValueType, strict_str_validator(value).strip())

    @abstractmethod
    def covers(self, value) -> bool:
        """Return ``True`` if input value is already covered by HWM"""
