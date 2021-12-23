from __future__ import annotations

import json

from pydantic import BaseModel as PydanticBaseModel
from pydantic.generics import GenericModel as PydanticGenericModel


class BaseModel(PydanticBaseModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    def serialize(self) -> dict:
        return json.loads(self.json(by_alias=True))

    @classmethod
    def deserialize(cls, inp: dict):
        return cls.parse_obj(inp)


class GenericModel(PydanticGenericModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    def serialize(self) -> dict:
        return json.loads(self.json(by_alias=True))

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
