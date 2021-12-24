from __future__ import annotations

from etl_entities.instance.path.generic_path import GenericPath


class AbsolutePath(GenericPath):
    """Absolute path representation

    Same as :obj:`pathlib.PurePosixPath`, but path can only start with ``/``
    """

    def __new__(cls, *args):
        self = super().__new__(cls, *args)

        if not self.is_absolute():
            raise ValueError(f"{cls.__name__} should start with '/'")

        return self
