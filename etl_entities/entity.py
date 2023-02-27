#  Copyright 2023 MTS (Mobile Telesystems)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
