# SPDX-FileCopyrightText: 2021-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, TypeVar

from typing_extensions import Protocol, runtime_checkable

try:
    from pydantic.v1 import validator
except (ImportError, AttributeError):
    from pydantic import validator  # type: ignore[no-redef, assignment]

from etl_entities.hwm import FileHWM
from etl_entities.hwm.hwm_type_registry import register_hwm_type

FileModifiedTimeHWMType = TypeVar("FileModifiedTimeHWMType", bound="FileModifiedTimeHWM")


@runtime_checkable
class StatWithMtime(Protocol):
    @property
    def st_mtime(self) -> float | None: ...  # noqa: E704


@runtime_checkable
class PathWithStats(Protocol):
    def is_file(self) -> bool: ...  # noqa: E704
    def exists(self) -> bool: ...  # noqa: E704
    def stat(self) -> StatWithMtime: ...  # noqa: E704


@register_hwm_type("file_modification_time")
class FileModifiedTimeHWM(FileHWM[Optional[datetime]]):  # noqa: WPS338r
    """HWM based on tracking file modification time.

    Uses ``Pathlib.Path(file).stat().st_mtime`` under the hood.

    .. warning::

        Some filesystems may return ``st_mtime`` rounded to whole second or even worse
        (some FTP servers round time to minutes, 10s of minutes or even hours). This could lead to skipping
        files created since previous process run, but having the same modification time as HWM value.

        Also this HWM should not be used if file modification time can be changed after the file
        was already handled by previous ETL process run. This could lead to reading the same file twice.

    .. versionadded:: 2.5.0

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : :obj:`datetime.datetime` or ``None``, default: ``None``

        HWM value

    directory : :obj:`pathlib.Path`, default: ``None``

        Directory for HWM value.

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        HWM expression

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    Examples
    --------

    .. code:: python

        from datetime import datetime, timezone
        from etl_entities.hwm import FileModifiedTimeHWM

        hwm = FileModifiedTimeHWM(
            name="hwm_name",
            value=datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc),
        )
    """

    value: Optional[datetime] = None

    @validator("value", pre=True)
    def _parse_isoformat(cls, value):  # noqa: N805
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    @validator("value")
    def _always_include_tz(cls, value: datetime | None):  # noqa: N805r
        if value and value.tzinfo is None:
            return value.astimezone()
        return value

    def covers(self, value: datetime | int | float | PathWithStats) -> bool:  # type: ignore
        """Return ``True`` if input value is already covered by HWM

        Examples
        --------

        >>> from pathlib import Path
        >>> from etl_entities.hwm import FileModifiedTimeHWM
        >>> hwm = FileModifiedTimeHWM(
        ...     name="hwm_name",
        ...     value=datetime(2025, 1, 1, 11, 22, 33, 456789),
        ... )
        >>> hwm.covers(Path("/some/old_file.py"))  # path not in HWM
        False
        """

        new_value: datetime | None
        if isinstance(value, PathWithStats):
            new_timestamp = value.stat().st_mtime if value.exists() and value.is_file() else None
            new_value = self._check_new_value(new_timestamp)
        else:
            new_value = self._check_new_value(value)

        return self.value is not None and new_value is not None and self.value.timestamp() >= new_value.timestamp()

    def update(
        self: FileModifiedTimeHWMType,
        value: datetime | int | float | PathWithStats | Iterable[PathWithStats],
    ) -> FileModifiedTimeHWMType:
        """Updates current HWM value with some implementation-specific logic, and return HWM.

        .. note::

            Changes HWM value in place

        Returns
        -------
        result : FileModifiedTimeHWM

            Self

        Examples
        --------

        >>> from pathlib import Path
        >>> from etl_entities.hwm import FileModifiedTimeHWM
        >>> hwm = FileModifiedTimeHWM(
        ...     name='hwm_name',
        ...     value=datetime(2025, 1, 1, 11, 22, 33, 456789),
        ... )
        >>> # old file is already covered
        >>> hwm.update(Path("/some/old_file.py")).value
        datetime.datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=...)
        """

        new_value: datetime | None = None
        if isinstance(value, Iterable):
            timestamps = [path.stat().st_mtime for path in value if path.exists() and path.is_file()]
            new_timestamp = max(filter(None, timestamps), default=None)
            new_value = self._check_new_value(new_timestamp)
        elif isinstance(value, PathWithStats):
            new_timestamp = value.stat().st_mtime if value.exists() and value.is_file() else None
            new_value = self._check_new_value(new_timestamp)
        else:
            new_value = self._check_new_value(value)

        if not self.value and new_value:
            return self.set_value(new_value)

        if self.value and new_value and self.value.timestamp() < new_value.timestamp():
            return self.set_value(new_value)

        return self

    def reset(self: FileModifiedTimeHWMType) -> FileModifiedTimeHWMType:
        """Reset current HWM value and return HWM.

        .. note::

            Changes HWM value in-place

        Returns
        -------
        result : FileModifiedTimeHWM

            Self

        Examples
        --------

        >>> from pathlib import Path
        >>> from etl_entities.hwm import FileModifiedTimeHWM
        >>> hwm = FileModifiedTimeHWM(
        ...     name='hwm_name',
        ...     value=datetime(2025, 1, 1, 11, 22, 33, 456789),
        ... )
        >>> hwm = hwm.reset()
        >>> hwm.value
        """
        return self.set_value(None)
