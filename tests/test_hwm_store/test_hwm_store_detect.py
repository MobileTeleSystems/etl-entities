import pytest
from omegaconf import OmegaConf

from etl_entities.hwm_store import (
    HWMStoreStackManager,
    MemoryHWMStore,
    detect_hwm_store,
    register_hwm_store_class,
)


@pytest.mark.parametrize(
    "config_value",
    [
        {},
        42,
        "string",
        None,
        [1, 2, 3],
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_invalid_configs(config_constructor, config_value):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    with pytest.raises((ValueError, TypeError)):
        conf = config_constructor(config_value)
        main(conf)


@pytest.mark.parametrize("invalid_key", [None, 123, []], ids=["None", "int", "list"])
def test_detect_hwm_store_invalid_key_input(invalid_key):
    with pytest.raises(ValueError, match="key name must be a string"):

        @detect_hwm_store(invalid_key)
        def main(config):  # NOSONAR
            pass


def test_detect_hwm_store_empty_key_input():
    with pytest.raises(ValueError, match="Key value must be specified"):

        @detect_hwm_store("")
        def main(config):  # NOSONAR
            pass


@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_multiple_hwm_store_types(config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):
        pass

    # Using two known HWM store types for demonstration.
    conf = config_constructor({"hwm_store": {"memory": None, "some_other_store": None}})

    with pytest.raises(ValueError, match="Multiple HWM store types provided: .*. Only one is allowed."):
        main(conf)


@pytest.mark.parametrize(
    "config, key",
    [
        ({"some_hwm": "value"}, "unknown_hwm"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "hwm1.hwm2.unknown_hwm"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "unknown_hwm.hwm2.hwm3"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "hwm1.unknown_hwm.hwm3"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "hwm1..hwm2"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "..hwm1.hwm2"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "hwm1.hwm2.."),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, ".hwm1.hwm2"),
        ({"hwm1": {"hwm2": {"hwm3": "value"}}}, "hwm1.hwm2."),
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_missing_key(config_constructor, config, key):
    with pytest.raises(ValueError, match=f"The configuration does not contain a required key {key!r}"):

        @detect_hwm_store(key)
        def main(input_config):
            ...  # noqa: WPS428

        conf = config_constructor(config)
        main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": "unknown"},
        {"hwm_store": {"unknown": None}},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_unknown_hwm(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    conf = config_constructor(input_config)
    with pytest.raises(KeyError, match="Unknown HWM Store type .*"):
        main(conf)


@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_wrong_options(config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    conf = config_constructor({"hwm_store": {"memory": ["too_many_arg"]}})

    # text error in python 3.12 version changed
    with pytest.raises(TypeError, match="1 positional argument"):
        main(conf)

    conf = config_constructor({"hwm_store": {"memory": {"unknown": "arg"}}})

    with pytest.raises(ValueError, match="extra fields not permitted"):
        main(conf)


@pytest.mark.parametrize(
    "input_config",
    [
        {"hwm_store": 123},
        {"hwm_store": ["memory", "other"]},
        {"hwm_store": None},
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_unsupported_value_type(input_config, config_constructor):
    @detect_hwm_store("hwm_store")
    def main(config):  # NOSONAR
        pass

    conf = config_constructor(input_config)
    with pytest.raises(ValueError, match="Wrong value .* for .* config item"):
        main(conf)


@pytest.mark.parametrize(
    "input_config, expected_args, expected_kwargs",
    [
        ({"hwm_store": {"custom": None}}, (), {}),
        ({"hwm_store": {"custom": "one_arg"}}, ("one_arg",), {}),
        ({"hwm_store": {"custom": ["arg1", "arg2"]}}, ("arg1", "arg2"), {}),
        ({"hwm_store": {"custom": {"arg1": "val1", "arg2": "val2"}}}, (), {"arg1": "val1", "arg2": "val2"}),
    ],
)
@pytest.mark.parametrize("config_constructor", [dict, OmegaConf.create])
def test_detect_hwm_store_custom_class(input_config, config_constructor, expected_args, expected_kwargs):
    @register_hwm_store_class("custom")
    class CustomHWMStore(MemoryHWMStore):
        args: tuple
        kwargs: dict

        def __init__(self, *args, **kwargs):
            object.__setattr__(self, "args", args)
            object.__setattr__(self, "kwargs", kwargs)

    @detect_hwm_store("hwm_store")
    def main(config):
        hwm_store = HWMStoreStackManager.get_current()
        assert isinstance(hwm_store, CustomHWMStore)
        assert hwm_store.args == expected_args
        assert hwm_store.kwargs == expected_kwargs

    conf = config_constructor(input_config)
    main(conf)
