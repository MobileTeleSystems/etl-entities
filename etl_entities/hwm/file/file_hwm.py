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
from abc import abstractmethod
from typing import Any, Generic, Iterable, TypeVar

from pydantic import Field, validator

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
    directory : :obj: `pathlib.PosixPath`

        Path to directory

    value : ``FileHWMValueType``

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    """

    entity: AbsolutePath = Field(alias="directory")
    value: FileHWMValueType
    name: str
    description: str = ""
    expression: Any = None

    class Config:  # noqa: WPS431
        json_encoders = {AbsolutePath: os.fspath}

    @validator("entity", pre=True)
    def validate_directory(cls, value):  # noqa: N805
        return AbsolutePath(value)

    @abstractmethod
    def update(self, value: str | os.PathLike | Iterable[str | os.PathLike]):
        """Updates current HWM value with some implementation-specific logic, and return HWM."""

    def __eq__(self, other):
        """Checks equality of two FileHWM instances

        Params
        -------
        other : :obj:`hwmlib.hwm.file_hwm.FileHWM`

        Returns
        --------
        result : bool

            ``True`` if both inputs are the same, ``False`` otherwise
        """

        if not isinstance(other, FileHWM):
            return False

        self_fields = self.dict(exclude={"modified_time"})
        other_fields = other.dict(exclude={"modified_time"})

        return self_fields == other_fields
