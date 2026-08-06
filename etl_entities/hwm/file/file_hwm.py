# SPDX-FileCopyrightText: 2023-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from abc import abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import ConfigDict, Field, field_validator

from etl_entities.hwm.file.absolute_path import AbsolutePath, parse_absolute_path
from etl_entities.hwm.hwm import HWM

FileHWMValueType = TypeVar("FileHWMValueType")


class FileHWM(  # noqa: PLW1641
    HWM[FileHWMValueType],
    Generic[FileHWMValueType],
):
    """Basic file HWM type

    Parameters
    ----------
    name : ``str``

        HWM unique name

    value : ``FileHWMValueType``

        HWM value

    directory : :obj:`pathlib.Path`, default: ``None``

        Directory HWM value is bound to. Should be an absolute path.

    description : ``str``, default: ``""``

        Description of HWM

    expression : Any, default: ``None``

        Expression used to generate HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    """

    entity: AbsolutePath | None = Field(default=None, alias="directory")
    value: FileHWMValueType

    model_config = ConfigDict(extra="forbid")

    @abstractmethod
    def covers(self, value: Any) -> bool:
        """Return ``True`` if input value is already covered by HWM"""

    def __eq__(self, other):
        """Checks equality of two FileHWM instances

        Parameters
        ----------
        other : :obj:`etl_entities.hwm.file_hwm.FileHWM`

        Returns
        -------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise
        """

        if not isinstance(other, type(self)):
            return NotImplemented

        self_fields = self.model_dump(exclude={"modified_time"}, warnings=False)
        other_fields = other.model_dump(exclude={"modified_time"}, warnings=False)

        return self_fields == other_fields

    @field_validator("entity", mode="before")
    @classmethod
    def _validate_directory(cls, value):
        if value is None:
            return None
        return parse_absolute_path(value)
