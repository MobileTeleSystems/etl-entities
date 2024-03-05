# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import ClassVar, Collection, TypeVar

from etl_entities.hwm_store.base_hwm_store import BaseHWMStore

T = TypeVar("T", bound=BaseHWMStore)


class HWMStoreClassRegistry:
    """Registry class of different HWM stores."""

    _default: type[BaseHWMStore | None] = type(None)
    _mapping: ClassVar[dict[str, type[BaseHWMStore]]] = {}

    @classmethod
    def get(cls, alias: str | None = None) -> type:
        """
        Return HWM Store class by its alias, or return default HWM Store class.

        Examples
        --------

        .. code:: python

            from etl_entities.hwm_store import HWMStoreClassRegistry, MemoryHWMStore

            HWMStoreClassRegistry.get("memory") == MemoryHWMStore

            HWMStoreClassRegistry.get("unknown")  # raise KeyError

            HWMStoreClassRegistry.get()  # some default HWM Store, see `set_default`

        """
        if not alias:
            return cls._default

        result = cls._mapping.get(alias)
        if not result:
            raise KeyError(f"Unknown HWM Store type {alias!r}")

        return result

    @classmethod
    def add(cls, alias: str, klass: type[BaseHWMStore]) -> None:
        """
        Add alias for HWM Store class.

        This alias then can be used by
        :obj:`detect_hwm_store <etl_entities.hwm_store.hwm_store_detect.detect_hwm_store>`.

        Examples
        --------

        .. code:: python

            from etl_entities.hwm_store import HWMStoreClassRegistry, BaseHWMStore

            HWMStoreClassRegistry.get("my_store")  # raise KeyError


            class MyHWMStore(BaseHWMStore): ...


            HWMStoreClassRegistry.add("my_store", MyHWMStore)
            HWMStoreClassRegistry.get("my_store") == MyHWMStore

        """
        assert isinstance(alias, str)  # noqa: S101
        assert issubclass(klass, BaseHWMStore)  # noqa: S101

        cls._mapping[alias] = klass

    @classmethod
    def set_default(cls, klass: type[BaseHWMStore]) -> None:
        """Set specific HWM store class as default HWM Store implementation.

        Examples
        --------

        .. code-block:: python

            from etl_entities.hwm_store import HWMStoreClassRegistry, BaseHWMStore


            class MyHWMStore(BaseHWMStore): ...


            HWMStoreClassRegistry.set_default(MyHWMStore)

            assert HWMStoreClassRegistry.get() == MyHWMStore

        """
        cls._default = klass

    @classmethod
    def aliases(cls) -> Collection[str]:
        """Returl all known HWM store aliases, like ``memory`` or ``yaml``"""
        return cls._mapping.keys()


def register_hwm_store_class(alias: str):
    """Decorator for registering some Store class with a name.

    Thin wrapper for :obj:`HWMStoreClassRegistry.add`.

    Examples
    --------

    .. code:: python

        from etl_entities.hwm_store import (
            HWMStoreClassRegistry,
            register_hwm_store_class,
            BaseHWMStore,
        )


        @register_hwm_store_class("my_store")
        class MyHWMStore(BaseHWMStore): ...


        HWMStoreClassRegistry.get("my_store") == MyHWMStore

    """

    def wrapper(cls: type[T]) -> type[T]:
        HWMStoreClassRegistry.add(alias, cls)
        return cls

    return wrapper
