# SPDX-FileCopyrightText: 2021-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import ClassVar

import typing_extensions

from etl_entities.process.process import Process


@typing_extensions.deprecated(
    "Deprecated in v2.0, will be removed in v3.0",
    category=UserWarning,
)
@dataclass
class ProcessStackManager:
    """
    Handles current stack of processes

    .. deprecated:: 2.0.0
    """

    with warnings.catch_warnings():  # noqa: WPS604
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
        --------

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
        -------
        process : :obj:`etl_entities.process.process.Process`

            Process instance. If stack is empty, ``IndexError`` will be raised

        Examples
        --------

        .. code:: python

            from etl_entities import ProcessStackManager

            process = ProcessStackManager.pop(process)
        """

        return cls._stack.pop()

    @classmethod
    def get_current_level(cls) -> int:
        """Returns number of processes in the stack

        Returns
        -------
        result : int

            Number of processes

        Examples
        --------

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
        --------

        .. code:: python

            from etl_entities import ProcessStackManager, Process

            with Process(name="mycolumn", host="myhost") as process:
                assert ProcessStackManager.get_current() == process

            assert ProcessStackManager.get_current() == Process()  # some default process
        """

        if cls._stack:
            return cls._stack[-1]

        return cls.default
