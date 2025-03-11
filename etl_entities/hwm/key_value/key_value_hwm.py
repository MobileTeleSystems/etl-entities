# SPDX-FileCopyrightText: 2021-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import sys
from typing import Generic, Optional, TypeVar

from frozendict import frozendict

try:
    from pydantic.v1 import Field, validator
except (ImportError, AttributeError):
    from pydantic import Field, validator  # type: ignore[no-redef, assignment]

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM

KeyValueHWMValueType = TypeVar("KeyValueHWMValueType")
KeyValueHWMKeyType = TypeVar("KeyValueHWMKeyType")
KeyValueHWMType = TypeVar("KeyValueHWMType", bound="KeyValueHWM")


class KeyValueHWM(HWM[frozendict], Generic[KeyValueHWMKeyType, KeyValueHWMValueType], GenericModel):
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

    entity: Optional[str] = Field(default=None, alias="topic")
    if sys.version_info >= (3, 9):  # noqa: WPS604
        value: frozendict[KeyValueHWMKeyType, KeyValueHWMValueType] = Field(default_factory=frozendict)
    else:
        value: frozendict = Field(default_factory=frozendict)

    def update(self: KeyValueHWMType, new_data: dict) -> KeyValueHWMType:
        """
        Updates the HWM value based on provided new key-value data. This method only updates
        the value if the new value is greater than the current valur for a given key
        or if the key does not exist in the current value.

        .. note::
            Changes the HWM value in place and returns the modified instance.

        Parameters
        ----------
        new_data : dict
            A dictionary representing new key-value data. For example: keys are partitions and values are offsets.

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
        >>> # Value for key 1 is not updated as 123 is less than current 125
        >>> hwm = hwm.update({1: 123})
        >>> hwm.value
        frozendict.frozendict({0: 100, 1: 125, 2: 130})
        """

        modified = False
        new_dict = {int(key): int(value) for key, value in new_data.items()}
        current_dict = dict(self.value)

        for new_key, new_value in new_dict.items():
            current_value = current_dict.get(new_key)
            if current_value is None or new_value > current_value:
                current_dict[new_key] = new_value
                modified = True

        # update the frozendict only if modifications were made.
        # this avoids unnecessary reassignment and creation of a new frozendict object,
        if modified:
            self.set_value(frozendict(current_dict))

        return self

    def reset(self: KeyValueHWMType) -> KeyValueHWMType:
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

        self_fields = self.dict(exclude={"modified_time"})
        other_fields = other.dict(exclude={"modified_time"})
        return self_fields == other_fields

    @validator("value", pre=True, always=True)
    def _convert_dict_to_frozendict(cls, v):  # noqa: N805
        if isinstance(v, dict):
            return frozendict(v)
        return v
