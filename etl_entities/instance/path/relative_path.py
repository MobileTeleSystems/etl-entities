#  Copyright 2022 MTS (Mobile Telesystems)
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

from etl_entities.instance.path.generic_path import GenericPath


class RelativePath(GenericPath):
    """Relative path representation

    Same as :obj:`pathlib.PurePosixPath`, but path cannot start with ``/``
    """

    def __new__(cls, *args):
        self = super().__new__(cls, *args)

        if self.is_absolute():
            raise ValueError(f"{cls.__name__} cannot start with '/'")

        if not self.parts:
            raise ValueError(f"{cls.__name__} cannot be empty")

        return self
