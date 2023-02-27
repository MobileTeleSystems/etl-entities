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
from typing import Generic, TypeVar

from etl_entities.entity import GenericModel
from etl_entities.hwm.hwm import HWM
from etl_entities.instance import AbsolutePath
from etl_entities.source import RemoteFolder

FileHWMValueType = TypeVar("FileHWMValueType")
FileHWMSerializedType = TypeVar("FileHWMSerializedType")


class FileHWM(
    HWM[FileHWMValueType, FileHWMSerializedType],
    GenericModel,
    Generic[FileHWMValueType, FileHWMSerializedType],
):
    """Basic file HWM type

    Parameters
    ----------
    source : :obj:`etl_entities.instance.path.remote_folder.RemoteFolder`

        Folder instance

    value : ``FileHWMValueType``

        HWM value

    modified_time : :obj:`datetime.datetime`, default: current datetime

        HWM value modification time

    process : :obj:`etl_entities.process.process.Process`, default: current process

        Process instance
    """

    source: RemoteFolder
    value: FileHWMValueType

    class Config:  # noqa: WPS431
        json_encoders = {AbsolutePath: os.fspath}

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Name of HWM
        """

    def __str__(self) -> str:
        """
        Returns full HWM name
        """

        return f"{self.name}#{self.source.full_name}"

    @property
    def qualified_name(self) -> str:
        """
        Unique name of HWM
        """

        return "#".join([self.name, self.source.qualified_name, self.process.qualified_name])

    def __bool__(self):
        """Check if HWM value is set

        Returns
        --------
        result : bool

            ``False`` if ``value`` is empty, ``True`` otherwise
        """

        return bool(self.value)

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
