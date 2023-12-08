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

import sys
from pathlib import PurePosixPath


class GenericPath(PurePosixPath):
    """Generic path representation without '..' and '~'."""

    def __init__(self, *args):
        # Call the parent class __init__ method

        # In Python 3.12 and later, paths are stored in _raw_paths.
        # For earlier versions, fall back to _parts.
        if sys.version_info >= (3, 12):
            super().__init__(*args)
        else:
            super().__init__()

        if ".." in self.parts or "~" in self.parts:
            raise ValueError(f"{self.__class__.__name__} cannot contain '..' or '~'")
