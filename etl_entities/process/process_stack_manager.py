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
#  limitations under the License.from __future__ import annotations

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from etl_entities.process.process import Process


@dataclass
class ProcessStackManager:
    """
    Handles current stack of processes
    """

    default: ClassVar[Process] = Process()  # noqa: WPS462
    "Default process returned by ``ProcessStackManager.get_current``"  # noqa: WPS428

    _stack: ClassVar[list[Process]] = []

    @classmethod
    def push(cls, process: Process) -> None:
        """Pushes a process to the stack

        Parameters
        ----------
        process : :obj:`etl_entities.process.process.Process`

            Process instance

        Examples
        ----------

        .. code:: python

            from etl_entities import ProcessStackManager, Process

            process = Process(name="mycolumn", host="myhost")
            ProcessStackManager.push(process)
        """

        cls._stack.append(process)

    @classmethod
    def pop(cls) -> Process:
        """Pops a process from the stack

        Returns
        ----------
        process : :obj:`etl_entities.process.process.Process`

            Process instance. If stack is empty, ``IndexError`` will be raised

        Examples
        ----------

        .. code:: python

            from etl_entities import ProcessStackManager

            process = ProcessStackManager.pop(process)
        """

        return cls._stack.pop()

    @classmethod
    def get_current_level(cls) -> int:
        """Returns number of processes in the stack

        Returns
        ----------
        result : int

            Number of processes

        Examples
        ----------

        .. code:: python

            from etl_entities import ProcessStackManager, Process

            with Process(name="mycolumn", host="myhost"):
                assert ProcessStackManager.get_current_level() == 1

            assert ProcessStackManager.get_current_level() == 0
        """

        return len(cls._stack)

    @classmethod
    def get_current(cls) -> Process:
        """Returns latest process in the stack or a default one

        Examples
        ----------

        .. code:: python

            from etl_entities import ProcessStackManager, Process

            with Process(name="mycolumn", host="myhost") as process:
                assert ProcessStackManager.get_current() == process

            assert ProcessStackManager.get_current() == Process()  # some default process
        """

        if cls._stack:
            return cls._stack[-1]

        return cls.default
