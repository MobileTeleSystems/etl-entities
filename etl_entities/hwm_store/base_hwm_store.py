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

import logging
from abc import ABC, abstractmethod
from typing import Any

from etl_entities.entity import BaseModel
from etl_entities.hwm import HWM
from etl_entities.hwm_utils import log_with_indent

log = logging.getLogger(__name__)


class BaseHWMStore(BaseModel, ABC):
    def __enter__(self):
        """
        HWM store context manager.

        Enter this context to use this HWM store instance as current one (instead default).

        Examples
        --------

        .. code:: python

            with hwm_store:
                db_reader.run()
        """
        # hack to avoid circular imports
        from etl_entities.hwm_store.hwm_store_manager import HWMStoreManager

        log.debug("|%s| Entered stack at level %d", self.__class__.__name__, HWMStoreManager.get_current_level())
        HWMStoreManager.push(self)

        self._log_parameters()
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        from etl_entities.hwm_store.hwm_store_manager import HWMStoreManager

        log.debug("|%s| Exiting stack at level %d", self, HWMStoreManager.get_current_level() - 1)
        HWMStoreManager.pop()
        return False

    @abstractmethod
    def get(self, name: str) -> HWM | None:
        """
        Get HWM by name from HWM store.

        Parameters
        ----------
        name : str
            HWM name

        Returns
        -------
        HWM object, if it exists in HWM store, or None

        Examples
        --------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            # just to generate name using HWM parts
            empty_hwm = ColumnIntHWM(column=..., name=..., ...)
            real_hwm = hwm_store.get(empty_hwm.name)
        """

    @abstractmethod
    def save(self, hwm: HWM) -> Any:
        """
        Save HWM object to HWM Store.

        Parameters
        ----------
        hwm : :obj:`etl_entities.hwm.HWM`
            HWM object

        Returns
        -------
        HWM location, like URL of file path.

        Examples
        --------

        .. code:: python

            from etl_entities.hwm import ColumnIntHWM

            hwm = ColumnIntHWM(value=..., column=..., name=...)
            hwm_location = hwm_store.save(hwm)
        """

    def _log_parameters(self) -> None:
        log.info("Using %s as HWM Store", self.__class__.__name__)
        options = self.dict(by_alias=True, exclude_none=True)

        if options:
            log.info("|%s| Using options:", self.__class__.__name__)
            for option, value in options.items():
                log_with_indent(log, "%s = %r", option, value)
