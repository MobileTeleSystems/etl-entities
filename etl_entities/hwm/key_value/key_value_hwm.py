# SPDX-FileCopyrightText: 2024-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import sys
from typing import Generic, TypeVar

from pydantic import Field, field_validator
from typing_extensions import Self

from etl_entities.hwm.hwm import HWM

if sys.version_info < (3, 15):
    from frozendict import frozendict

KeyValueHWMValueType = TypeVar("KeyValueHWMValueType")
KeyValueHWMKeyType = TypeVar("KeyValueHWMKeyType")
KeyValueHWMType = TypeVar("KeyValueHWMType", bound="KeyValueHWM")


class KeyValueHWM(HWM[frozendict], Generic[KeyValueHWMKeyType, KeyValueHWMValueType]):  # noqa: PLW1641
    """HWM type storing ``key -> value`` map.

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``frozendict[KeyValueHWMKeyType, KeyValueHWMValueType]`` , default: ``frozendict``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    entity : Any, default: ``None``

        HWM entity, e.g. ``topic`` name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``offset``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time
    """

    entity: str | None = Field(default=None, alias="topic")
    value: frozendict[KeyValueHWMKeyType, KeyValueHWMValueType] = Field(default_factory=frozendict)

    def update(self, new_data: dict) -> Self:
        """
        Updates the HWM value based on provided new key-value data.

        .. note::
            Changes the HWM value in place and returns the modified instance.

        Parameters
        ----------
        new_data : dict
            A dictionary representing new key-value data.
            For example: keys are partitions and values are offsets.

        Returns
        -------
        self : KeyValueHWM
            The instance with updated HWM value.

        Examples
        --------

        >>> from frozendict import frozendict
        >>> from etl_entities.hwm import KeyValueHWM
        >>> hwm = KeyValueHWM(value={0: 100, 1: 120}, name="my_hwm")
        >>> hwm = hwm.update({1: 125, 2: 130})
        >>> hwm.value
        frozendict.frozendict({0: 100, 1: 125, 2: 130})
        """

        new = dict(self.value)
        new.update(new_data)
        self.set_value(frozendict(new))
        return self

    def reset(self) -> Self:
        """Reset current HWM value and return HWM.

        .. note::

            Changes HWM value in-place

        Returns
        -------
        result : KeyValueHWM

            Self

        Examples
        --------

        >>> from etl_entities.hwm import KeyValueHWM
        >>> hwm = KeyValueHWM(value={0: 100, 1: 120}, name="my_hwm")
        >>> hwm = hwm.reset()
        >>> dict(hwm.value)
        {}
        """
        return self.set_value(frozendict())

    def __eq__(self, other):
        """Checks equality of two HWM instances

        Parameters
        ----------
        other : :obj:`etl_entities.hwm.key_value.key_value_hwm.KeyValueHWM`

            You can compare two :obj:`etl_entities.hwm.key_value.key_value_hwm.KeyValueHWM` instances,
            obj:`etl_entities.hwm.key_value.key_value_hwm.KeyValueHWM` with an :obj:`object`,
            if its value is comparable with the ``value`` attribute of HWM

        Returns
        -------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        self_fields = self.model_dump(exclude={"modified_time"}, warnings=False)
        other_fields = other.model_dump(exclude={"modified_time"}, warnings=False)
        return self_fields == other_fields

    @field_validator("value", mode="before")
    @classmethod
    def _convert_dict_to_frozendict(cls, v):
        if isinstance(v, dict):
            return frozendict(v)
        return v
