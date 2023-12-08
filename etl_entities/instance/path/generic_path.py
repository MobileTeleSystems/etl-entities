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

import os
import sys
from pathlib import PurePosixPath


class GenericPath(PurePosixPath):
    """Generic path representation without '..' and '~'."""

    def __new__(cls, *args):
        if sys.version_info >= (3, 12):
            # for Python 3.12 and later
            self = super().__new__(cls)
            self._initialize_path_3_12(*args)
        else:
            self = super().__new__(cls, *args)

        # Validate the path parts
        parts_check = self.parts if sys.version_info >= (3, 12) else self._parts
        if ".." in parts_check or "~" in parts_check:
            raise ValueError(f"{cls.__name__} cannot contain '..' or '~'")

        return self

    def _initialize_path_3_12(self, *args):  # noqa: WPS114
        # Path initialization specifically for Python 3.12+
        paths = []
        for arg in args:
            if isinstance(arg, PurePosixPath):
                paths.extend(arg._raw_paths)  # noqa: WPS437
            else:
                path = str(os.fspath(arg)) if not isinstance(arg, str) else arg
                paths.append(path)
        self._raw_paths = paths
