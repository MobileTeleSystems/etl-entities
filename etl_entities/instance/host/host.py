# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from pydantic import AnyUrl, ConstrainedStr, parse_obj_as


class Host(ConstrainedStr):
    """Generic host representation"""

    min_length = 1

    @classmethod
    def validate(cls, value: str) -> str:
        url = parse_obj_as(AnyUrl, f"http://{value}")  # NOSONAR
        if url.host != value:
            raise ValueError(f"Invalid host {value}")

        return value
