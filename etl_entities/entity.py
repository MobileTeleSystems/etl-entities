from __future__ import annotations

from pydantic import BaseModel as PydanticBaseModel
from pydantic.generics import GenericModel as PydanticGenericModel


class BaseModel(PydanticBaseModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True


class GenericModel(PydanticGenericModel):
    class Config:  # noqa: WPS431
        frozen = True
        arbitrary_types_allowed = True


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
