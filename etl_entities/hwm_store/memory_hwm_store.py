# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Dict

try:
    from pydantic.v1 import PrivateAttr
except (ImportError, AttributeError):
    from pydantic import PrivateAttr  # type: ignore[no-redef, assignment]

from etl_entities.hwm import HWM
from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry
from etl_entities.hwm_store.base_hwm_store import BaseHWMStore
from etl_entities.hwm_store.hwm_store_class_registry import register_hwm_store_class


@register_hwm_store_class("memory")
class MemoryHWMStore(BaseHWMStore):
    """Simple in-memory (RAM) HWM Store.

    Alias: ``memory``

    .. note::

        All values stored in MemoryHWMStore are gone after the Python interpreter is exited.
        This class should be used in tests only!

    Examples
    --------

    >>> from etl_entities.hwm_store import MemoryHWMStore
    >>> from etl_entities.hwm import ColumnIntHWM
    >>> hwm_store = MemoryHWMStore()
    >>> retrieved_hwm = hwm_store.get_hwm("long_unique_name")
    >>> hwm_store.get_hwm("long_unique_name") # not found
    >>> hwm = ColumnIntHWM(name="long_unique_name", value=10)
    >>> hwm_store.set_hwm(hwm)
    >>> got_hwm = hwm_store.get_hwm("long_unique_name") # found
    >>> got_hwm == hwm
    True
    >>> hwm_store.clear()
    >>> hwm_store.get_hwm("long_unique_name") # not found again
    """

    _data: Dict[str, dict] = PrivateAttr(default_factory=dict)

    class Config:  # noqa: WPS431
        extra = "forbid"

    def get_hwm(self, name: str) -> HWM | None:
        if name not in self._data:
            return None

        return HWMTypeRegistry.parse(self._data[name])

    def set_hwm(self, hwm: HWM) -> None:
        # avoid storing raw HWM objects because they can be changed implicitly
        self._data[hwm.name] = hwm.serialize()

    def clear(self) -> None:
        """
        Clears all stored HWM values.
        """
        self._data.clear()
