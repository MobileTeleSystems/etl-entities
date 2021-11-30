from __future__ import annotations

from typing import Generic, TypeVar, cast

from pydantic import Field, validator
from pydantic.validators import str_validator

from hwmlib.entity import Entity, GenericModel
from hwmlib.process import Process, ProcessStackManager

T = TypeVar("T")


class HWM(Entity, GenericModel, Generic[T]):
    """Generic HWM type

    Parameters
    ----------
    value : Any

        HWM value of any type

    process : :obj:`hwmlib.process.process.Process`, default: current process

        Process instance
    """

    value: T
    process: Process = Field(default_factory=ProcessStackManager.get_current)

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, str):
            return cls.deserialize(value)

        return value

    def serialize(self) -> str:
        """Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from hwmlib import HWM

            hwm = HWM(value=1, ...)
            assert hwm.serialize() == "1"
        """

        return str(self.value).strip()

    @classmethod
    def deserialize(cls, value: str) -> T:
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

            from hwmlib import IntHWM

            assert IntHWM.deserialize("123") == 123
        """

        return cast(T, str_validator(value).strip())

    def with_value(self, value: T) -> HWM:
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

            from hwmlib import IntHWM

            hwm = IntHWM(value=1, ...)
            new_hwm = hwm.with_value(2)

            assert new_hwm.value == 2
        """

        dct = self.dict()
        dct["value"] = value
        return self.parse_obj(dct)
