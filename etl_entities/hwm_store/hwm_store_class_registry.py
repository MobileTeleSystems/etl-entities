# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import ClassVar, Collection, TypeVar

from etl_entities.hwm_store.base_hwm_store import BaseHWMStore

T = TypeVar("T", bound=BaseHWMStore)


class HWMStoreClassRegistry:
    """Registry class of different HWM stores.

    Examples
    --------

    .. code:: python

        from etl_entities.hwm_store import HWMStoreClassRegistry, MemoryHWMStore

        HWMStoreClassRegistry.get("memory") == MemoryHWMStore

        HWMStoreClassRegistry.get("unknown")  # raise KeyError

    """

    _default: type[BaseHWMStore | None] = type(None)
    _mapping: ClassVar[dict[str, type[BaseHWMStore]]] = {}

    @classmethod
    def get(cls, type_name: str | None = None) -> type:
        if not type_name:
            return cls._default

        result = cls._mapping.get(type_name)
        if not result:
            raise KeyError(f"Unknown HWM Store type {type_name!r}")

        return result

    @classmethod
    def add(cls, type_name: str, klass: type[BaseHWMStore]) -> None:
        assert isinstance(type_name, str)  # noqa: S101
        assert issubclass(klass, BaseHWMStore)  # noqa: S101

        cls._mapping[type_name] = klass

    @classmethod
    def set_default(cls, klass: type[BaseHWMStore]) -> None:
        cls._default = klass

    @classmethod
    def known_types(cls) -> Collection[str]:
        return cls._mapping.keys()


def register_hwm_store_class(type_name: str):
    """Decorator for registering some Store class with a name

    Examples
    --------

    .. code:: python

        from etl_entities.hwm_store import (
            HWMStoreClassRegistry,
            register_hwm_store_class,
            BaseHWMStore,
        )


        @register_hwm_store_class("somename")
        class MyClass(BaseHWMStore): ...


        HWMStoreClassRegistry.get("somename") == MyClass

    """

    def wrapper(cls: type[T]) -> type[T]:
        HWMStoreClassRegistry.add(type_name, cls)
        return cls

    return wrapper
