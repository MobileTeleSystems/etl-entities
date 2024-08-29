# SPDX-FileCopyrightText: 2021-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
# isort: skip_file

from __future__ import annotations

import json

try:
    from pydantic.v1 import BaseModel as PydanticBaseModel
    from pydantic.v1.generics import GenericModel as PydanticGenericModel
except (ImportError, AttributeError):
    from pydantic import BaseModel as PydanticBaseModel  # type: ignore[no-redef, assignment]
    from pydantic.generics import GenericModel as PydanticGenericModel  # type: ignore[no-redef, assignment]


class BaseModel(PydanticBaseModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    def serialize(self) -> dict:
        return json.loads(self.json())

    @classmethod
    def deserialize(cls, inp: dict):
        return cls.parse_obj(inp)


class GenericModel(PydanticGenericModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    def serialize(self) -> dict:
        return json.loads(self.json())

    @classmethod
    def deserialize(cls, inp: dict):
        return cls.parse_obj(inp)


class Entity:
    """
    Generic entity representation
    """

    @property
    def qualified_name(self) -> str:
        """
        Unique entity name
        """

        return str(self)
