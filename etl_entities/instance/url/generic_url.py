# SPDX-FileCopyrightText: 2021-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from typing import ClassVar

try:
    from pydantic.v1 import AnyUrl
except (ImportError, AttributeError):
    from pydantic import AnyUrl


class GenericURL(AnyUrl):
    """Generic URL representation

    .. warning::

        ``user``, ``password``, ``query`` and ``fragment`` parts are not allowed
    """

    PROHIBITED_PARTS: ClassVar[tuple[str, ...]] = ("user", "password", "query", "fragment")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.PROHIBITED_PARTS:
            if getattr(self, field):
                msg = f"URL cannot contain {field} field"
                raise ValueError(msg)
