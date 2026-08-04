# SPDX-FileCopyrightText: 2024-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import Mapping

from frozendict import frozendict
from pydantic import field_validator
from typing_extensions import Self

from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry, register_hwm_type
from etl_entities.hwm.key_value.key_value_hwm import KeyValueHWM


@register_hwm_type("key_value_int")
class KeyValueIntHWM(KeyValueHWM[int, int]):
    """HWM type storing ``int -> int`` mapping.

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``frozendict[int, int]``, default: ``frozendict``

        HWM value

    description : ``str``, default: ``""``

        Description of HWM

    entity : Any, default: ``None``

        HWM entity, e.g. topic name

    expression : Any, default: ``None``

        Expression used to generate HWM value, e.g. ``offset``

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    --------

    .. code:: python

        from etl_entities.hwm import KeyValueIntHWM

        hwm_kv_int = KeyValueIntHWM(
            name="long_unique_name",
            source="topic_name",
            expression="offset",
            value={
                0: 100,  # 0 and 1 - partition numbers
                1: 123,  # 100 and 123 - offset values
            },
        )
    """

    def serialize(self) -> dict:
        result = self.model_dump(mode="json", exclude={"value"}, warnings=False)
        result["value"] = dict(self.value)
        result["type"] = HWMTypeRegistry.get_key(self.__class__)
        return result

    @field_validator("value", mode="before")
    @classmethod
    def _validate_int_values(cls, key_value):
        if isinstance(key_value, Mapping):
            result = {}
            for key, value in key_value.items():
                if not isinstance(key, (int, str)):
                    msg = f"key should be integer, got {key!r}"
                    raise ValueError(msg)  # noqa: TRY004

                if not isinstance(value, (int, str)):
                    msg = f"Value should be integer, got {value!r}"
                    raise ValueError(msg)  # noqa: TRY004

                result[int(key)] = int(value)
            return frozendict(result)

        return key_value

    def update(self, new_data: dict) -> Self:
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
        self : KeyValueIntHWM
            The instance with updated HWM value.

        Examples
        --------

        >>> from frozendict import frozendict
        >>> from etl_entities.hwm import KeyValueIntHWM
        >>> hwm = KeyValueIntHWM(value={0: 100, 1: 120}, name="my_hwm")
        >>> hwm = hwm.update({1: 125, 2: 130})
        >>> hwm.value
        frozendict.frozendict({0: 100, 1: 125, 2: 130})
        >>> # Value for key 1 is not updated as 123 is less than current 125
        >>> hwm = hwm.update({1: 123})
        >>> hwm.value
        frozendict.frozendict({0: 100, 1: 125, 2: 130})
        """

        modified = False
        current_dict = {int(key): int(value) for key, value in self.value.items()}
        new_dict = {int(key): int(value) for key, value in new_data.items()}

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
