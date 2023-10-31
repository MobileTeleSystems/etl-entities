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

from collections.abc import Sequence
from functools import wraps
from typing import Any, Callable, Mapping

from etl_entities.hwm_store.hwm_store_class_registry import HWMStoreClassRegistry


def parse_config(value: Any, key: str) -> tuple[str, Sequence, Mapping]:
    if not isinstance(value, (str, Mapping)):
        raise ValueError(f"Wrong value {value!r} for {key!r} config item")

    store_type = "unknown"
    args: Sequence[Any] = []
    kwargs: Mapping[str, Any] = {}

    if isinstance(value, str):
        return value, args, kwargs

    # If more than one store type detected, raise error
    if len(value) > 1:
        raise ValueError(f"Multiple HWM store types provided: {', '.join(value)}. Only one is allowed.")

    for item in HWMStoreClassRegistry.known_types():
        if item not in value:
            continue

        store_type = item
        child = value[item]

        args, kwargs = parse_child_item(child)

    return store_type, args, kwargs


def parse_child_item(child: Any) -> tuple[Sequence, Mapping]:
    store_args: Sequence[Any] = []
    store_kwargs: Mapping[str, Any] = {}

    if child is None:
        return store_args, store_kwargs

    if isinstance(child, Mapping):
        store_kwargs = child
    elif isinstance(child, Sequence) and not isinstance(child, str):
        store_args = child
    else:
        store_args = [child]

    return store_args, store_kwargs


def resolve_attr(conf: Mapping, hwm_key: str) -> Any:
    obj = {}

    try:
        if "." not in hwm_key:
            obj = conf[hwm_key]
        else:
            for name in hwm_key.split("."):
                obj = conf[name]
                conf = obj
    except Exception as e:
        raise ValueError(f"The configuration does not contain a required key {hwm_key!r}") from e

    return obj


def detect_hwm_store(key: str) -> Callable:
    """Detect HWM store by config object

    Parameters
    ----------
    key : str
        The name of the section in the config that stores information about hwm

        .. warning ::

            **DO NOT** use dot ``.`` in config keys

    Examples
    --------

    Config

    .. code:: yaml

        # if HWM store can be created with no args
        hwm_store: yaml

    or

    .. code:: yaml

        # named constructor args
        hwm_store:
            atlas:
                url: http://some.atlas.url
                user: username
                password: password

    Config could be nested:

    .. code:: yaml

        myetl:
            env:
                hwm_store: yaml

    ``run.py``

    .. code:: python

        import hydra
        from omegaconf import DictConfig
        from etl_entities.hwm_store import detect_hwm_store


        # key=... is a path to config item, delimited by dot ``.``
        @hydra.main(config="../conf")
        @detect_hwm_store(key="myetl.env.hwm_store")
        def main(config: DictConfig):
            pass

    """

    if not isinstance(key, str):
        raise ValueError("key name must be a string")

    if not key:
        raise ValueError("Key value must be specified")

    def pre_wrapper(func: Callable):  # noqa: WPS430
        @wraps(func)
        def wrapper(config: Mapping, *args, **kwargs):
            if not config:
                raise ValueError("Config must be specified")

            root = resolve_attr(config, key)
            store_type, store_args, store_kwargs = parse_config(root, key)
            store = HWMStoreClassRegistry.get(store_type)

            with store(*store_args, **store_kwargs):
                return func(config, *args, **kwargs)

        return wrapper

    return pre_wrapper
