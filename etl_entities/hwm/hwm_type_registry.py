# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from bidict import bidict

if TYPE_CHECKING:
    from etl_entities.hwm.hwm import HWM


class HWMTypeRegistry:
    """Registry class for HWM types"""

    _mapping: ClassVar[bidict[str, type[HWM]]] = bidict()

    @classmethod
    def get(cls, type_name: str) -> type[HWM]:
        """Get HWM class by type name

        Parameters
        ----------
        type_name : str

            Type name

        Examples
        --------

        >>> from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM, ColumnDateHWM
        >>> HWMTypeRegistry.get("column_int")
        <class 'etl_entities.hwm.column.int_hwm.ColumnIntHWM'>
        >>> HWMTypeRegistry.get("column_date")
        <class 'etl_entities.hwm.column.date_hwm.ColumnDateHWM'>
        >>> HWMTypeRegistry.get("unknown")
        Traceback (most recent call last):
            ...
        KeyError: "Unknown HWM type 'unknown'"
        """

        result = cls._mapping.get(type_name)
        if not result:
            raise KeyError(f"Unknown HWM type {type_name!r}")

        return result

    @classmethod
    def get_key(cls, klass: type[HWM]) -> str:
        """Get HWM type name for a class

        Parameters
        ----------
        klass : obj:`type`

            HWM class

        Examples
        --------

        >>> from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM, ColumnDateHWM, HWM
        >>> HWMTypeRegistry.get_key(ColumnIntHWM)
        'column_int'
        >>> HWMTypeRegistry.get_key(ColumnDateHWM)
        'column_date'
        >>> class UnknownHWM(HWM): ...
        >>> HWMTypeRegistry.get_key(UnknownHWM)
        Traceback (most recent call last):
            ...
        KeyError: "You should register 'UnknownHWM' class using @register_hwm_type decorator"
        """

        result = cls._mapping.inverse.get(klass)
        if not result:
            raise KeyError(f"You should register {klass.__qualname__!r} class using @register_hwm_type decorator")

        return result

    @classmethod
    def add(cls, type_name: str, klass: type[HWM]) -> None:
        """Add mapping ``HWM class`` -> ``type name`` to registry

        Parameters
        ----------
        type_name : :obj:`str`

            Type name

        klass : :obj:`type`

            HWM class

        Examples
        --------

        >>> from etl_entities.hwm import HWMTypeRegistry, HWM
        >>> class MyHWM(HWM): ...
        >>> HWMTypeRegistry.add("my_hwm", MyHWM)
        >>> HWMTypeRegistry.get("my_hwm")
        <class 'etl_entities.hwm.hwm_type_registry.MyHWM'>
        """

        cls._mapping[type_name] = klass

    @classmethod
    def parse(cls, inp: dict) -> HWM:
        """Parse HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        --------

        >>> from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM
        >>> hwm = HWMTypeRegistry.parse(
        ...     {
        ...         "type": "column_int",
        ...         "name": "some_name",
        ...         "value": "1",
        ...         "entity": "some_entity",
        ...         "description": "some description",
        ...     }
        ... )
        >>> type(hwm)
        <class 'etl_entities.hwm.column.int_hwm.ColumnIntHWM'>
        >>> hwm.name
        'some_name'
        >>> hwm.value
        1
        >>> hwm.entity
        'some_entity'
        >>> hwm.description
        'some description'
        >>> HWMTypeRegistry.parse({"type": "unknown"})
        Traceback (most recent call last):
            ...
        KeyError: "Unknown HWM type 'unknown'"
        """

        klass = cls.get(inp["type"])
        return klass.deserialize(inp)


def register_hwm_type(type_name: str):
    """Decorator register some HWM class with a type name

    Examples
    --------

    >>> from etl_entities.hwm import HWMTypeRegistry, register_hwm_type, ColumnHWM
    >>> @register_hwm_type("my_hwm")
    ... class MyHWM(ColumnHWM): ...
    >>> HWMTypeRegistry.get("my_hwm")
    <class 'etl_entities.hwm.hwm_type_registry.MyHWM'>
    >>> hwm = HWMTypeRegistry.parse(
    ...     {
    ...         "type": "my_hwm",
    ...         "name": "some_name",
    ...         "value": 1,
    ...         "entity": "some_entity",
    ...         "description": "some description",
    ...     },
    ... )
    >>> type(hwm)
    <class 'etl_entities.hwm.hwm_type_registry.MyHWM'>
    >>> hwm.name
    'some_name'
    >>> hwm.value
    1
    >>> hwm.entity
    'some_entity'
    >>> hwm.description
    'some description'
    """

    def wrapper(klass):
        HWMTypeRegistry.add(type_name, klass)
        return klass

    return wrapper
