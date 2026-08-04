# SPDX-FileCopyrightText: 2021-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import sys
from pathlib import PurePosixPath


class AbsolutePath(PurePosixPath):
    """Absolute path representation

    Same as :obj:`pathlib.PurePosixPath`, but path can only start with ``/``
    """

    def __init__(self, *args):
        if sys.version_info >= (3, 12):
            super().__init__(*args)
        else:
            super().__init__()

        if ".." in self.parts or "~" in self.parts:
            msg = f"{self.__class__.__name__} cannot contain '..' or '~'"
            raise ValueError(msg)

        if not self.is_absolute():
            msg = f"{self.__class__.__name__} should start with '/'"
            raise ValueError(msg)
