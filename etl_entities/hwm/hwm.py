from __future__ import annotations

import json
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
    def deserialize(cls, inp: dict) -> HWM:
        """Return HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            assert (
                IntHWM.deserialize(
                    {
                        "value": "1",
                        "type": "int",
                        "column": {"name": ..., "partition": ...},
                        "source": ...,
                        "process": ...,
                    }
                )
                == IntHWM(value=1, ...)
            )

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

    def with_value(self, value: ValueType) -> HWM:
        """Create copy of HWM object with specified value

        Parameters
        ----------
        value : Any

            New HWM value

        Returns
        -------
        result : HWM

            Copy of HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import IntHWM

            hwm = IntHWM(value=1, ...)
            new_hwm = hwm.with_value(2)

            assert new_hwm.value == 2
        """

        dct = self.dict()
        dct["value"] = value
        dct["modified_time"] = datetime.now()
        return self.parse_obj(dct)
