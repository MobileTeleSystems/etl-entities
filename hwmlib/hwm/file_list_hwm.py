from __future__ import annotations

import os
from pathlib import PosixPath, PurePosixPath
from typing import FrozenSet, Iterable

from pydantic import Field, validator

from hwmlib.hwm.hwm import HWM
from hwmlib.location import RelativePath
from hwmlib.source import RemoteFolder


class FileListHWM(HWM):
    """File List HWM type

    Parameters
    ----------
    folder : :obj:`hwmlib.location.path.remote_folder.RemoteFolder`

        Folder instance

    value : :obj:`frosenset` of :obj:`pathlib.PosixPath`, default: empty set

        HWM value

    process : :obj:`hwmlib.process.process.Process`, default: current process

        Process instance

    Examples
    ----------

    .. code:: python

        from hwmlib import FileListHWM, RemoteFolder

        folder = RemoteFolder(root="/root/path", location="postgres://db.host:5432")

        hwm = FileListHWM(
            folder=folder,
            value=["some/path", "another.file"],
        )
    """

    folder: RemoteFolder
    value: FrozenSet[RelativePath] = Field(default_factory=frozenset)

    @validator("value", pre=True)
    def validate_value(cls, value):  # noqa: N805
        if isinstance(value, (str, PosixPath, PurePosixPath)):
            return cls.deserialize(os.fspath(value))

        if isinstance(value, Iterable):
            return frozenset(RelativePath(item) for item in value)

        return super().validate_value(value)

    @property
    def name(self) -> str:
        """
        Name of HWM
        """

        return "downloaded_files"

    @property
    def qualified_name(self) -> str:
        """
        Unique name of HWM
        """

        return "#".join([self.name, self.folder.qualified_name, self.process.qualified_name])

    def serialize(self) -> str:
        r"""Return string representation of HWM value

        Returns
        -------
        result : str

            Serialized value

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM

            hwm = FileListHWM(value=["some/file.py", "another.file"], ...)
            assert hwm.serialize() == "some/file.py\nanother.file"

            hwm = FileListHWM(value=[], ...)
            assert hwm.serialize() == ""
        """

        return "\n".join(sorted(os.fspath(item) for item in self.value))

    @classmethod
    def deserialize(cls, value: str) -> frozenset[RelativePath]:  # noqa: E800
        r"""Parse string representation to get HWM value

        Parameters
        ----------
        value : str

            Serialized value

        Returns
        -------
        result : :obj:`frozenset` of :obj:`hwmlib.location.path.relative_path.RelativePath`

            Deserialized value

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM

            assert FileListHWM.deserialize("some/path.py\nanother.file") == frosenset(
                RelativePath("some/path.py"), RelativePath("another.file")
            )

            assert FileListHWM.deserialize([]) == frosenset()
        """

        value = super().deserialize(value)

        if value:
            return frozenset(RelativePath(item.strip()) for item in value.split("\n"))

        return frozenset()

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is empty, ``True`` otherwise

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM

            hwm = FileListHWM(value=["some/path.py"], ...)
            assert hwm  # same as bool(hwm.value)

            hwm = FileListHWM(value=[], ...)
            assert not hwm
        """

        return bool(self.value)

    def __add__(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Creates copy of HWM with added value

        Params
        -------
        value : :obj:`str` or :obj:`pathlib.PosixPath` or :obj:`typing.Iterable` of them

            Path or collection of paths to be added to value

        Returns
        --------
        result : HWM

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM

            hwm1 = FileListHWM(value=["some/path"], ...)
            hwm2 = FileListHWM(value=["some/path", "another.file"], ...)

            assert hwm1 + "another.file" == hwm2
            # same as FileListHWM(value=hwm1.value + "another.file", ...)
        """

        values: Iterable[RelativePath]
        if isinstance(value, Iterable):
            values = (RelativePath(item) for item in value)
        else:
            values = [RelativePath(value)]

        return self.with_value(self.value.union(values))

    def __abs__(self):
        """Returns list of files with absolute paths

        Returns
        --------
        result : :obj:`frosenzet` of :obj:`pathlib.PosixPath`

            Copy of HWM with updated value

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], folder=Folder(root="/root/path", ...), ...)

            assert abs(hwm) == frosenset(AbsolutePath("/root/path/some/path"))
        """

        return frozenset(self.folder.root / item for item in self.value)

    def __contains__(self, item):
        """Checks if path is present in value

        Returns
        --------
        result : bool

            ``True`` if path is present in value, ``False`` otherwise

        Examples
        ----------

        .. code:: python

            from hwmlib import FileListHWM, Folder, AbsolutePath

            hwm = FileListHWM(value=["some/path"], folder=Folder(root="/root/path", ...), ...)

            assert "some/path" in hwm
            assert "/root/path/some/path" in hwm
        """

        if not isinstance(item, os.PathLike):
            item = PurePosixPath(item)

        return item in self.value or item in abs(self)
