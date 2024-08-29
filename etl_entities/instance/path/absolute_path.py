# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import sys

from etl_entities.instance.path.generic_path import GenericPath


class AbsolutePath(GenericPath):
    """Absolute path representation

    Same as :obj:`pathlib.PurePosixPath`, but path can only start with ``/``
    """

    def __init__(self, *args):
        if sys.version_info >= (3, 12):
            super().__init__(*args)
        else:
            super().__init__()

        if not self.is_absolute():
            raise ValueError(f"{self.__class__.__name__} should start with '/'")
