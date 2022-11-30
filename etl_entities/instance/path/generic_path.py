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

from pathlib import PurePosixPath


class GenericPath(PurePosixPath):
    """Generic path representation

    Same as :obj:`pathlib.PurePosixPath`, but `..` are not allowed
    """

    def __new__(cls, *args):
        self = super().__new__(cls, *args)

        if ".." in self.parts or "~" in self.parts:
            raise ValueError(f"{cls.__name__} cannot contain '..' or '.'")

        return self
