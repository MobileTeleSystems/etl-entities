# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections import deque
from typing import ClassVar

from etl_entities.hwm_store.base_hwm_store import BaseHWMStore
from etl_entities.hwm_store.hwm_store_class_registry import HWMStoreClassRegistry


class HWMStoreStackManager:
    """
    Class used to store stack of entered HWM Store context managers.
    """

    _stack: ClassVar[deque[BaseHWMStore]] = deque()

    @classmethod
    def push(cls, hwm_store: BaseHWMStore) -> None:
        """Push HWM Store object to stack"""
        cls._stack.append(hwm_store)

    @classmethod
    def pop(cls) -> BaseHWMStore:
        """Pop latest HWM Store object from stack"""
        return cls._stack.pop()

    @classmethod
    def get_current_level(cls) -> int:
        """Get current number of objects in the stack"""
        return len(cls._stack)

    @classmethod
    def get_current(cls) -> BaseHWMStore:
        """
        Get HWM Store implementation set by context manager.

        Examples
        --------

        >>> from etl_entities.hwm_store import HWMStoreStackManager
        >>> with SomeHWMStore(...) as hwm_store:
        ...     print(HWMStoreStackManager.get_current())
        SomeHWMStore(...)
        >>> HWMStoreStackManager.get_current()
        DefaultHWMStore()
        """
        if cls._stack:
            return cls._stack[-1]

        default_store_type = HWMStoreClassRegistry.get()
        return default_store_type()
