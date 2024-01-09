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
from typing import Generic, Optional, TypeVar

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

        Params
        -------
        other : :obj:`etl_entities.hwm.file_hwm.FileHWM`

        Returns
        --------
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
