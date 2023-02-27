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
from typing import Union

from pydantic import validator

from etl_entities.entity import BaseModel, Entity
from etl_entities.instance import AbsolutePath, Cluster, GenericPath, GenericURL

# folder path cannot have delimiters used in qualified_name
PROHIBITED_PATH_SYMBOLS = "@#"


class RemoteFolder(BaseModel, Entity):
    """Remote folder representation

    Parameters
    ----------
    name : :obj:`str` or :obj:`pathlib.PosixPath`

        Folder path

        .. warning::

            Only absolute path without ``..`` are allowed

    instance : :obj:`etl_entities.instance.url.generic_url.GenericURL`

        Instance URL in format ``"protocol://some.domain[:port]"``

    Examples
    ----------

    .. code:: python

        from etl_entities import RemoteFolder

        folder1 = RemoteFolder(name="/absolute/folder", instance="rnd-dwh")
        folder2 = RemoteFolder(name="/absolute/folder", instance="ftp://some.domain:10000")
    """

    name: AbsolutePath
    instance: Union[GenericURL, Cluster]

    class Config:  # noqa: WPS431
        json_encoders = {AbsolutePath: os.fspath}

    @validator("name", pre=True)
    def check_absolute_path(cls, value):  # noqa: N805
        value = AbsolutePath(value)

        for symbol in PROHIBITED_PATH_SYMBOLS:
            if symbol in str(value):
                raise ValueError(f"Folder name cannot contain symbols {' '.join(PROHIBITED_PATH_SYMBOLS)}")

        return value

    @property
    def full_name(self):
        """
        Full folder name

        Returns
        ----------
        value : str

            Folder full name

        Examples
        ----------

        .. code:: python

            from etl_entities import RemoteFolder

            folder = RemoteFolder(name="/absolute/folder", instance="rnd-dwh")

            assert folder.full_name == "/absolute/folder"
        """

        return os.fspath(self.name)

    def __str__(self):
        """
        Returns full process name
        """

        return self.full_name

    def __truediv__(self, path: GenericPath) -> AbsolutePath:
        """
        Returns absolute path for nested file or folder
        """

        return self.name / path

    @property
    def qualified_name(self) -> str:
        """
        Unique name of remote folder

        Returns
        ----------
        value : str

            Qualified name

        Examples
        ----------

        .. code:: python

            from etl_entities import RemoteFolder

            folder1 = RemoteFolder(name="/absolute/folder", instance="rnd-dwh")
            folder2 = RemoteFolder(name="/absolute/folder", instance="ftp://some.domain:10000")

            assert folder1.qualified_name == "/absolute/folder@rnd-dwh"
            assert folder1.qualified_name == "/absolute/folder@ftp://some.domain:10000"
        """

        return "@".join([str(self), str(self.instance)])
