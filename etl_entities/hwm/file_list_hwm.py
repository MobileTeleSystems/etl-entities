from __future__ import annotations

import os
from pathlib import PosixPath, PurePosixPath
from typing import FrozenSet, Iterable

from pydantic import Field, validator

from etl_entities.hwm.file_hwm import FileHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type
from etl_entities.instance import AbsolutePath, RelativePath

FileListType = FrozenSet[RelativePath]


@register_hwm_type("files_list")
class FileListHWM(FileHWM[FileListType]):
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
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, (str, PosixPath, PurePosixPath)):
            return cls.deserialize_value(os.fspath(value))

        if isinstance(value, Iterable):
            return frozenset(RelativePath(item) for item in value)

        return super().validate_value(value)

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

    def serialize_value(self) -> str:
        r"""Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm = FileListHWM(value=["some/file.py", "another.file"], ...)
            assert hwm.serialize_value() == "some/file.py\nanother.file"

            hwm = FileListHWM(value=[], ...)
            assert hwm.serialize_value() == ""
        """

        return "\n".join(sorted(os.fspath(item) for item in self.value))

    @classmethod
    def deserialize_value(cls, value: str) -> FileListType:  # noqa: E800
        r"""Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`frozenset` of :obj:`etl_entities.instance.path.relative_path.RelativePath`

            Deserialized value

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            assert FileListHWM.deserialize_value("some/path.py\nanother.file") == frozenset(
                RelativePath("some/path.py"), RelativePath("another.file")
            )

            assert FileListHWM.deserialize_value([]) == frozenset()
        """

        str_value: str = super().deserialize_value(value)  # type: ignore[assignment]

        if str_value:
            return frozenset(RelativePath(item.strip()) for item in str_value.split("\n"))

        return frozenset()

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
        """Updates current HWM value with some implementation-specific login, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : HWM

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

        return self + value

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

    def __add__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Adds path or paths to HWM value, and return updated HWM

        .. note::

            Changes HWM value in place instead of returning new one

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : FileListHWM

            Self

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 + "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value + "another.file", ...)
        """

        self.set_value(self.value | self.validate_value(value))
        return self

    def __sub__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Remove path or paths from HWM value, and return updated HWM

        .. note::

            Changes HWM value in place instead of returning new one

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : FileListHWM

            Self

        Examples
        ----------

        .. code:: python

            from etl_entities import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 - "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value - "another.file", ...)
        """

        self.set_value(self.value - self.validate_value(value))
        return self

    def __abs__(self) -> frozenset[AbsolutePath]:
        """Returns list of files with absolute paths

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
