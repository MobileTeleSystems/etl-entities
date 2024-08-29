# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0


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
