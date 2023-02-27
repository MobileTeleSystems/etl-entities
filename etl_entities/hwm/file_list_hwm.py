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

import os
from pathlib import PurePosixPath
from typing import FrozenSet, Iterable, List

from pydantic import Field, validator

from etl_entities.hwm.file_hwm import FileHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.instance import AbsolutePath, RelativePath

FileListType = FrozenSet[RelativePath]


@register_hwm_type("file_list")
class FileListHWM(FileHWM[FileListType, List[str]]):
    """File List HWM type

    Parameters
    ----------
    source : :obj:`etl_entities.instance.path.remote_folder.RemoteFolder`

        Folder instance

    value : :obj:`frozenset` of :obj:`pathlib.PosixPath`, default: empty set

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from etl_entities import FileListHWM, RemoteFolder

        folder = RemoteFolder(name="/absolute/path", instance="ftp://ftp.server:21")

        hwm = FileListHWM(
            source=folder,
            value=["some/path", "another.file"],
        )
    """

    value: FileListType = Field(default_factory=frozenset)

    class Config:  # noqa: WPS431
        json_encoders = {RelativePath: os.fspath}

    @validator("value", pre=True)
    def validate_value(cls, value, values):  # noqa: N805
        if "source" not in values:
            raise ValueError("Missing `source` key")

        source = values["source"]

        if isinstance(value, (os.PathLike, str)):
            return cls.deserialize_value([value], source.name)

        if isinstance(value, Iterable):
            return cls.deserialize_value(value, source.name)

        return value

    @property
    def name(self) -> str:
        """
        Name of HWM

        Returns
        ----------
        value : str

            Static value ``"file_list"``
        """

        return "file_list"

    def serialize_value(self) -> list[str]:
        """Return JSON representation of HWM value

        Returns
        -------
        result : list[str]

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/file.py", "another.file"], ...)
            assert hwm.serialize_value() == ["some/file.py", "another.file"]

            hwm = FileListHWM(value=[], ...)
            assert hwm.serialize_value() == []
        """

        return sorted(os.fspath(item) for item in self.value)

    @classmethod
    def deserialize_value(
        cls,
        value: list[str],
        remote_folder: AbsolutePath,
    ) -> FileListType:
        """Parse JSON representation to get HWM value

        Parameters
        ----------
        value : list[str]

            Serialized value

        Returns
        -------
        result : :obj:`frozenset` of :obj:`etl_entities.instance.path.relative_path.RelativePath`

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            assert FileListHWM.deserialize_value(["some/path.py", "another.file"]) == frozenset(
                RelativePath("some/path.py"), RelativePath("another.file")
            )

            assert FileListHWM.deserialize_value([]) == frozenset()
        """

        result = []

        for item in value:
            path = PurePosixPath(os.fspath(item).strip())
            if path.is_absolute():
                path = path.relative_to(remote_folder)

            result.append(RelativePath(path))

        return frozenset(result)

    def covers(self, value: str | os.PathLike) -> bool:
        """Return ``True`` if input value is already covered by HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/path.py"], ...)

            assert hwm.covers("some/path.py")  # path in HWM
            assert not hwm.covers("another/path.py")  # path not in HWM
        """

        return value in self

    def update(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Updates current HWM value with some implementation-specific logic, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : FileListHWM

            Self

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/existing_path.py"], ...)

            # new paths are appended
            hwm.update("some/new_path.py")
            assert hwm.value == [
                "some/existing_path.py",
                "some/new_path.py",
            ]

            # existing paths do nothing
            hwm.update("some/existing_path.py")
            assert hwm.value == [
                "some/existing_path.py",
                "some/new_path.py",
            ]
        """

        new_value = self.value | self._check_new_value(value)
        if self.value != new_value:
            return self.set_value(new_value)

        return self

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is empty, ``True`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/path.py"], ...)
            assert hwm  # same as bool(hwm.value)

            hwm = FileListHWM(value=[], ...)
            assert not hwm
        """

        return bool(self.value)

    def __len__(self):
        """Return number of files in the HWM.

        Returns
        --------
        result : int

            Number of files

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some", "another"], ...)
            hwm2 = FileListHWM(value=[], ...)

            assert len(hwm1) == 2
            assert len(hwm2) == 0
        """

        return len(self.value)

    def __add__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Adds path or paths to HWM value, and return copy of HWM

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : FileListHWM

            HWM copy with new value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 + "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value + "another.file", ...)
        """

        new_value = self.value | self._check_new_value(value)
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __sub__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Remove path or paths from HWM value, and return copy of HWM

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : FileListHWM

            HWM copy with new value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 - "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value - "another.file", ...)
        """

        new_value = self.value - self._check_new_value(value)
        if self.value != new_value:
            return self.copy().set_value(new_value)

        return self

    def __iter__(self):
        """Iterate over files in FileListHWM.

        Returns
        --------
        result : Iterator[RelativePath]

            Files in HWM, order is not preserved

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM, RelativePath

            hwm1 = FileListHWM(value=["some", "another"], ...)
            hwm2 = FileListHWM(value=[], ...)

            assert set(hwm1) == {RelativePath("some"), RelativePath("another")}
            assert set(hwm2) == set()
        """

        return iter(self.value)

    def __abs__(self) -> frozenset[AbsolutePath]:
        """Returns set of files with absolute paths

        Returns
        --------
        result : :obj:`frosenzet` of :obj:`pathlib.PosixPath`

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], source=Folder(name="/absolute/path", ...), ...)

            assert abs(hwm) == frozenset(AbsolutePath("/absolute/path/some/path"))
        """

        return frozenset(self.source / item for item in self.value)

    def __contains__(self, item):
        """Checks if path is present in value

        Returns
        --------
        result : bool

            ``True`` if path is present in value, ``False`` otherwise

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], source=Folder(name="/absolute/path", ...), ...)

            assert "some/path" in hwm
            assert "/absolute/path/some/path" in hwm
        """

        if not isinstance(item, os.PathLike):
            item = PurePosixPath(item)

        return item in self.value or item in abs(self)

    def __eq__(self, other):
        """Checks equality of two FileListHWM instances

        Params
        -------
        other : :obj:`hwmlib.hwm.file_list_hwm.FileListHWM`

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise.

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some"], ...)
            hwm2 = FileListHWM(value=["another"], ...)

            assert hwm1 == hwm1
            assert hwm1 != hwm2
        """

        if not isinstance(other, FileListHWM):
            return False

        return super().__eq__(other)
