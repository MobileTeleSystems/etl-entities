#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import annotations

from typing import ClassVar, Collection

from etl_entities.hwm_store.base_hwm_store import BaseHWMStore


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
        class MyClass(BaseHWMStore):
            ...


        HWMStoreClassRegistry.get("somename") == MyClass

    """

    def wrapper(cls: type[BaseHWMStore]):
        HWMStoreClassRegistry.add(type_name, cls)
        return cls

    return wrapper
