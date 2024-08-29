# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
import sys
from typing import FrozenSet, Iterable, TypeVar

try:
    from pydantic.v1 import Field, validator
except (ImportError, AttributeError):
    from pydantic import Field, validator  # type: ignore[no-redef, assignment]

from etl_entities.hwm import FileHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.instance import AbsolutePath

FileListType = FrozenSet[AbsolutePath]
FileListHWMType = TypeVar("FileListHWMType", bound="FileListHWM")


@register_hwm_type("file_list")
class FileListHWM(FileHWM[FileListType]):
    """File List HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : :obj:`set` of :obj:`pathlib.Path`, default: empty set

        HWM value

    directory : :obj:`pathlib.Path`, default: ``None``

        Directory for HWM value. All paths in ``value`` must be relative to this directory.

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    --------

    .. code:: python

        from etl_entities.hwm import FileListHWM
        from etl_entities.instance import AbsolutePath

        hwm = FileListHWM(
            name="hwm_name",
            value={"/some/path", "/another.file"},
        )
    """

    value: FileListType = Field(default_factory=frozenset)

    def covers(self, value: str | os.PathLike) -> bool:  # type: ignore
        """Return ``True`` if input value is already covered by HWM

        Examples
        --------

        >>> from etl_entities.hwm import FileListHWM
        >>> hwm = FileListHWM(value={"/some/path.py"}, name="my_hwm")
        >>> hwm.covers("/some/path.py")  # path in HWM
        True
        >>> hwm.covers("/another/path.py")  # path not in HWM
        False
        """

        return value in self

    def update(self: FileListHWMType, value: str | os.PathLike | Iterable[str | os.PathLike]) -> FileListHWMType:
        """Updates current HWM value with some implementation-specific logic, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : FileHWM

            Self

        Examples
        --------

        >>> from etl_entities.hwm import FileListHWM
        >>> hwm = FileListHWM(value=["/some/existing_path.py"], name="my_hwm")
        >>> # new paths are appended
        >>> hwm = hwm.update("/some/new_path.py")
        >>> sorted(hwm.value)
        [AbsolutePath('/some/existing_path.py'), AbsolutePath('/some/new_path.py')]
        >>> # existing path already here
        >>> hwm = hwm.update("/some/existing_path.py")
        >>> sorted(hwm.value)
        [AbsolutePath('/some/existing_path.py'), AbsolutePath('/some/new_path.py')]
        """

        new_value = self.value | self._check_new_value(value)
        if self.value != new_value:
            return self.set_value(new_value)

        return self

    def __add__(self: FileListHWMType, value: str | os.PathLike | Iterable[str | os.PathLike]) -> FileListHWMType:
        """Adds path or paths to HWM value, and return copy of HWM

        Parameters
        ----------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        -------
        result : FileListHWM

            HWM copy with new value

        Examples
        --------

        >>> from etl_entities.hwm import FileListHWM
        >>> hwm = FileListHWM(value={"/some/path"}, name="my_hwm")
        >>> hwm = hwm + "/another.file"
        >>> sorted(hwm.value)
        [AbsolutePath('/another.file'), AbsolutePath('/some/path')]
        """

        new_value = self.value | self._check_new_value(value)
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __sub__(self: FileListHWMType, value: str | os.PathLike | Iterable[str | os.PathLike]) -> FileListHWMType:
        """Remove path or paths from HWM value, and return copy of HWM

        Parameters
        ----------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        -------
        result : FileListHWM

            HWM copy with new value

        Examples
        --------

        >>> from etl_entities.hwm import FileListHWM
        >>> hwm = FileListHWM(value={"/some/path", "/another.file"}, name="my_hwm")
        >>> hwm = hwm - "/another.file"
        >>> sorted(hwm.value)
        [AbsolutePath('/some/path')]
        """

        new_value = self.value - self._check_new_value(value)
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __contains__(self, item):
        """Checks if path is present in value

        Returns
        -------
        result : bool

            ``True`` if path is present in value, ``False`` otherwise

        Examples
        --------

        >>> from etl_entities.hwm import FileListHWM
        >>> from etl_entities.instance import AbsolutePath
        >>> hwm = FileListHWM(value={"/some/path"}, name="my_hwm")
        >>> "/some/path" in hwm
        True
        >>> "/another/path" in hwm
        False
        """

        if isinstance(item, str):
            if not item.startswith("/"):
                return False

            item = AbsolutePath(item)

        return item in self.value

    @validator("value", pre=True)
    def _validate_value(cls, value, values: dict):  # noqa: N805
        directory = values.get("entity")
        if isinstance(value, (os.PathLike, str)):
            return cls._deserialize_value([value], directory)

        if isinstance(value, Iterable):
            return cls._deserialize_value(value, directory)

        return value

    @classmethod
    def _deserialize_value(
        cls,
        value: Iterable[str | os.PathLike],
        directory: str | os.PathLike | None,
    ) -> frozenset[AbsolutePath]:
        data = []

        for item in value:
            if not isinstance(item, AbsolutePath):
                item = AbsolutePath(item)

            if directory:
                if sys.version_info >= (3, 9):
                    if not item.is_relative_to(directory):
                        raise ValueError(f"Item {item} is not within directory {directory}")  # noqa: WPS220
                else:
                    item.relative_to(directory)

            data.append(item)

        return frozenset(data)
