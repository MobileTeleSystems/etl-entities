from __future__ import annotations

from typing import ClassVar, Tuple

from pydantic import AnyUrl


class GenericURL(AnyUrl):
    """Generic URL representation

    .. warning::

        ``user``, ``password``, ``query`` and ``fragment`` parts are not allowed
    """

    PROHIBITED_PARTS: ClassVar[Tuple[str, ...]] = ("user", "password", "query", "fragment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.PROHIBITED_PARTS:
            if getattr(self, field):
                raise ValueError(f"URL cannot contain {field} field")
