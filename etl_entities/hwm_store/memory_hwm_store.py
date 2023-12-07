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

from typing import Dict

from pydantic import PrivateAttr

from etl_entities.hwm import HWM
from etl_entities.hwm.hwm_type_registry import HWMTypeRegistry
from etl_entities.hwm_store.base_hwm_store import BaseHWMStore
from etl_entities.hwm_store.hwm_store_class_registry import register_hwm_store_class


@register_hwm_store_class("memory")
class MemoryHWMStore(BaseHWMStore):
    """In-memory local store for HWM values.

    .. note::

        This class should be used in tests only, because all saved HWM values
        will be deleted after exiting the context

    Examples
    --------

    .. code:: python
        from etl_entities.hwm_store import MemoryHWMStore
        from etl_entities.hwm import ColumnIntHWM

        hwm_store = MemoryHWMStore()

        # not found
        retrieved_hwm = hwm_store.get_hwm("long_unique_name")
        assert hwm_store.get_hwm("long_unique_name") is None

        hwm = ColumnIntHWM(name="long_unique_name", value=10)
        hwm_store.set_hwm(hwm_value)

        # found
        retrieved_hwm = hwm_store.get_hwm("long_unique_name")
        assert retrieved_hwm == hwm

        hwm_store.clear()
        # not found again
        assert hwm_store.get_hwm("long_unique_name") is None
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
