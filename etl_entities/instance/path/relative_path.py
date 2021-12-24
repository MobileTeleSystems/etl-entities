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
