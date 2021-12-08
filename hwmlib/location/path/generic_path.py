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
