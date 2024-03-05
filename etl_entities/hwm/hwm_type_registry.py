# SPDX-FileCopyrightText: 2021-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from bidict import bidict

if TYPE_CHECKING:
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

            from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM, ColumnDateHWM

            assert HWMTypeRegistry.get("int") == ColumnIntHWM
            assert HWMTypeRegistry.get("date") == ColumnDateHWM

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

            from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM, ColumnDateHWM

            assert HWMTypeRegistry.get_key(ColumnIntHWM) == "int"
            assert HWMTypeRegistry.get_key(ColumnDateHWM) == "date"

            HWMTypeRegistry.get_key(UnknownHWM)  # raises KeyError
        """

        result = cls._mapping.inverse.get(klass)
        if not result:
            raise KeyError(f"You should register {klass} class using @register_hwm_type decorator")

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

            from etl_entities.hwm import HWMTypeRegistry, HWM


            class MyHWM(HWM): ...


            HWMTypeRegistry.add("my_hwm", MyHWM)

            assert HWMTypeRegistry.get("my_hwm") == MyHWM
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
        --------

        .. code:: python

            from etl_entities.hwm import HWMTypeRegistry, ColumnIntHWM

            hwm = HWMTypeRegistry.parse(
                {
                    "type": "column_int",
                    "name": "some_name",
                    "value": "1",
                }
            )
            assert hwm == ColumnIntHWM(name="some_name", value=1)

            HWMTypeRegistry.parse({"type": "unknown"})  # raises KeyError
        """

        klass = cls.get(inp["type"])
        return klass.deserialize(inp)


def register_hwm_type(type_name: str):
    """Decorator register some HWM class with a type name

    Examples
    --------

    .. code:: python

        from etl_entities.hwm import HWMTypeRegistry, register_hwm_type, HWM


        @register_hwm_type("my_hwm")
        class MyHWM(HWM): ...


        assert HWMTypeRegistry.get("my_hwm") == MyHWM

        hwm = HWMTypeRegistry.parse(
            {
                "type": "my_hwm",
                "name": "some_name",
                "value": "1",
            }
        )
        assert hwm == MyHWM(name="some_name", value=1)

    """

    def wrapper(klass):
        HWMTypeRegistry.add(type_name, klass)
        return klass

    return wrapper
