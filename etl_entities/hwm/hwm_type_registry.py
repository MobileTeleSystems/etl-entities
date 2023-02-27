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

from typing import ClassVar

from bidict import bidict

from etl_entities.hwm.hwm import HWM


class HWMTypeRegistry:
    """Registry class for HWM types"""

    _mapping: ClassVar[bidict[str, type[HWM]]] = bidict()

    @classmethod
    def get(cls, type_name: str) -> type[HWM]:
        """Get HWM class by type name

        Parameters
        ----------
        type_name : str

            Type name

        Examples
        --------

        .. code:: python

            from etl_entities import HWMTypeRegistry, IntHWM, FloatHWM

            assert HWMTypeRegistry.get("int") == IntHWM
            assert HWMTypeRegistry.get("integer") == IntHWM  # multiple type names are supported

            assert HWMTypeRegistry.get("float") == FloatHWM

            HWMTypeRegistry.get("unknown")  # raises KeyError
        """

        result = cls._mapping.get(type_name)
        if not result:
            raise KeyError(f"Unknown HWM type {type_name}")

        return result

    @classmethod
    def get_key(cls, klass: type[HWM]) -> str:
        """Get HWM type name for a class

        Parameters
        ----------
        klass : obj:`type`

            HWM class

        Examples
        --------

        .. code:: python

            from etl_entities import HWMTypeRegistry, IntHWM, FloatHWM

            assert HWMTypeRegistry.get_key(IntHWM) == "int"  # only first type name is returned
            assert HWMTypeRegistry.get_key(FloatHWM) == "float"

            HWMTypeRegistry.get_key(UnknownHWM)  # raises KeyError
        """

        result = cls._mapping.inverse.get(klass)
        if not result:
            raise KeyError(f"You should registered {klass} class using @register_hwm_type decorator")

        return result

    @classmethod
    def add(cls, type_name: str, klass: type[HWM]) -> None:
        """Add mapping ``HWM class`` -> ``type name`` to registry

        Parameters
        ----------
        type_name : :obj:`str`

            Type name

        klass : :obj:`type`

            HWM class

        Examples
        --------

        .. code:: python

            from etl_entities import HWMTypeRegistry, HWM


            class MyHWM(HWM):
                ...


            HWMTypeRegistry.add("somename", MyHWM)
            HWMTypeRegistry.add("anothername", MyHWM)  # multiple type names are allowed

            assert HWMTypeRegistry.get("somename") == MyHWM
            assert HWMTypeRegistry.get("anothername") == MyHWM
        """

        cls._mapping[type_name] = klass

    @classmethod
    def parse(cls, inp: dict) -> HWM:
        """Parse HWM from dict representation

        Returns
        -------
        result : HWM

            Deserialized HWM

        Examples
        ----------

        .. code:: python

            from etl_entities import HWMTypeRegistry, IntHWM

            assert HWMTypeRegistry.parse(
                {
                    "value": "1",
                    "type": "int",
                    "column": {"name": ..., "partition": ...},
                    "source": ...,
                    "process": ...,
                }
            ) == IntHWM(value=1, ...)

            HWMTypeRegistry.parse({"type": "unknown"})  # raises KeyError
        """

        klass = cls.get(inp["type"])
        return klass.deserialize(inp)


def register_hwm_type(type_name: str):
    """Decorator for registering some HWM class with a type name

    Examples
    --------

    .. code:: python

        from etl_entities import HWMTypeRegistry, register_hwm_type, HWM


        @register_hwm_type("somename")
        class MyHWM(HWM):
            ...


        assert HWMTypeRegistry.get("somename") == MyHWM

    """

    def wrapper(klass: type[HWM]):
        HWMTypeRegistry.add(type_name, klass)
        return klass

    return wrapper
