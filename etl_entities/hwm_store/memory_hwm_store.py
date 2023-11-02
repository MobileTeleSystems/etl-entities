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

        hwm_value = ColumnIntHWM(name="example", column="sample_column", value=10)
        hwm_store.set_hwm(hwm_value)

        retrieved_hwm = hwm_store.get_hwm("example")
        assert retrieved_hwm == hwm_value

        hwm_store.clear()
        assert hwm_store.get_hwm("example") is None
    """

    _data: Dict[str, HWM] = PrivateAttr(default_factory=dict)

    class Config:  # noqa: WPS431
        extra = "forbid"

    def get_hwm(self, name: str) -> HWM | None:
        return self._data.get(name, None)

    def set_hwm(self, hwm: HWM) -> None:
        # TODO: replace with hwm.name after removing property "qualified_name" in HWM class
        self._data[hwm.qualified_name] = hwm

    def clear(self) -> None:
        """
        Clears all stored HWM values.
        """
        self._data.clear()
