# SPDX-FileCopyrightText: 2021-present MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Annotated

from pydantic import AfterValidator, TypeAdapter

if TYPE_CHECKING:
    import os


def validate(path: PurePosixPath):
    if not path.is_absolute():
        msg = "AbsolutePath should start with '/'"
        raise ValueError(msg)
    return path


AbsolutePath = Annotated[PurePosixPath, AfterValidator(validate)]
AbsolutePathAdapter = TypeAdapter(AbsolutePath)


def parse_absolute_path(path: str | os.PathLike) -> AbsolutePath:
    try:
        return AbsolutePathAdapter.validate_python(path)
    except TypeError as e:
        raise ValueError(*e.args) from e
