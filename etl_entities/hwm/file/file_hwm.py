# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from abc import abstractmethod
from typing import Generic, Optional, TypeVar

try:
    from pydantic.v1 import Field, validator
except (ImportError, AttributeError):
    from pydantic import Field, validator  # type: ignore[no-redef, assignment]

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM
from etl_entities.instance import AbsolutePath

FileHWMValueType = TypeVar("FileHWMValueType")


class FileHWM(
    HWM[FileHWMValueType],
    Generic[FileHWMValueType],
    GenericModel,
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

    entity: Optional[AbsolutePath] = Field(default=None, alias="directory")
    value: FileHWMValueType

    class Config:  # noqa: WPS431
        json_encoders = {AbsolutePath: os.fspath}

    @abstractmethod
    def covers(self, value: FileHWMValueType) -> bool:
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

        self_fields = self.dict(exclude={"modified_time"})
        other_fields = other.dict(exclude={"modified_time"})

        return self_fields == other_fields

    @validator("entity", pre=True)
    def _validate_directory(cls, value):  # noqa: N805
        if value is None:
            return None
        return AbsolutePath(value)
