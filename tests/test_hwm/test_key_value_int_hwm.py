import secrets
from datetime import datetime, timedelta

import pytest
from frozendict import frozendict

from etl_entities.hwm import KeyValueIntHWM


@pytest.mark.parametrize(
    "expression, value, expected_value",
    [
        ("offset", {0: 100, 1: 200}, frozendict({0: 100, 1: 200})),
        ("offset", {0: "100", 1: "200"}, frozendict({0: 100, 1: 200})),
        ("offset", {"key1": 100, "key2": 200}, frozendict({"key1": 100, "key2": 200})),
        ("offset", {"key1": "100", "key2": "200"}, frozendict({"key1": 100, "key2": 200})),
        (None, {}, frozendict()),
    ],
)
def test_key_value_int_hwm_valid_input(expression, value, expected_value):
    name = "key_value_int_hwm_name"
    entity = "topic_name"
    modified_time = datetime.now() - timedelta(days=5)

    empty_hwm = KeyValueIntHWM(name=name)
    assert empty_hwm.name == name
    assert empty_hwm.value == frozendict()

    minimal_hwm = KeyValueIntHWM(name=name, value=value)
    assert minimal_hwm.name == name
    assert minimal_hwm.value == expected_value

    hwm_with_duplicates = KeyValueIntHWM(name=name, value={**value, **value})
    assert hwm_with_duplicates.name == name
    assert hwm_with_duplicates.value == expected_value

    hwm = KeyValueIntHWM(
        name=name,
        value=value,
        description="my hwm",
        entity=entity,
        expression="something",
        modified_time=modified_time,
    )
    assert hwm.name == name
    assert hwm.value == expected_value
    assert hwm.description == "my hwm"
    assert hwm.entity == entity
    assert hwm.expression == "something"
    assert hwm.modified_time == modified_time


@pytest.mark.parametrize(
    "invalid_value",
    [
        {1: 1.5},
        {1: "offset_value"},
        {"partition": "offset_value"},
        {1: None},
        None,
    ],
)
def test_key_value_int_hwm_wrong_input(invalid_value):
    valid_value = {0: 100, 1: 123}
    name = "key_value_int_hwm_name"

    with pytest.raises(ValueError):
        # missing name
        KeyValueIntHWM()

    with pytest.raises(ValueError):
        # missing name
        KeyValueIntHWM(value=valid_value)

    with pytest.raises(ValueError):
        # invalid_dict
        KeyValueIntHWM(name=name, value=invalid_value)

    with pytest.raises(ValueError):
        # extra fields not allowed
        KeyValueIntHWM(name=name, unknown="unknown")


def test_key_value_int_hwm_set_value():
    name = "key_value_int_hwm_name"
    value1 = {0: 10}
    value2 = {0: 10, 1: 20}
    value3 = {0: 10, 1: 20, 2: 30}
    value = {0: 100, 1: 123}

    hwm = KeyValueIntHWM(name=name)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert hwm1.value == frozendict(value)
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm.copy()
    hwm2.set_value(value1)
    assert hwm2.value == frozendict(value1)
    assert hwm2.modified_time > hwm.modified_time

    hwm3 = hwm.copy()
    hwm3.set_value(value2)
    assert hwm3.value == frozendict(value2)
    assert hwm3.modified_time > hwm.modified_time

    hwm4 = hwm.copy()
    hwm4.set_value(value3)
    assert hwm4.value == frozendict(value3)
    assert hwm4.modified_time > hwm.modified_time

    with pytest.raises(ValueError):
        # invalid dict
        hwm.set_value({1: None})


def test_key_value_int_hwm_frozen():
    value1 = {0: 10}
    value2 = {0: 10, 1: 20}
    value3 = {0: 10, 1: 20, 2: 30}
    value = {0: 100, 1: 123}
    name = "key_value_int_hwm_name"
    modified_time = datetime.now() - timedelta(days=5)

    hwm = KeyValueIntHWM(name=name)

    for attr in ("value", "entity", "expression", "description", "modified_time"):
        for item in (1, "abc", None, value1, value2, value3, value, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_key_value_int_hwm_compare():
    name1 = secrets.token_hex()
    name2 = secrets.token_hex()
    entity = "topic_name"

    value1 = {0: 10}
    value2 = {0: 10, 1: 20}

    hwm1 = KeyValueIntHWM(name=name1, value=value1)
    hwm2 = KeyValueIntHWM(name=name2, value=value1)
    hwm3 = KeyValueIntHWM(name=name1, value=value2)
    hwm4 = KeyValueIntHWM(name=name2, value=value2)

    hwm5 = KeyValueIntHWM(name=name1, entity=entity)
    hwm6 = KeyValueIntHWM(name=name1, entity=entity + entity)

    hwm7 = KeyValueIntHWM(name=name1, description="abc")
    hwm8 = KeyValueIntHWM(name=name1, description="bcd")

    hwm9 = KeyValueIntHWM(name=name1, expression="abc")
    hwm10 = KeyValueIntHWM(name=name1, expression="bcd")

    modified_time = datetime.now() - timedelta(days=5)
    hwm_with_different_mtime = KeyValueIntHWM(name=name1, value=value1, modified_time=modified_time)

    # modified time is ignored when comparing
    assert hwm1 == hwm_with_different_mtime

    items = (hwm1, hwm2, hwm3, hwm4, hwm5, hwm6, hwm7, hwm8, hwm9, hwm10)

    # items with different attribute values (except modified_time) are not equal
    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2

    # this was true until 2.1.x, but not anymore
    for item in items:
        assert item != item.value


def test_key_value_int_hwm_update():
    hwm = KeyValueIntHWM(name="test_hwm", value=frozendict({1: 100, 2: 150}))
    original_modified_time = hwm.modified_time

    # update with new key, higher value, and lower value
    hwm.update({3: 200, 2: 180, 1: 50})
    assert hwm.value == frozendict({1: 100, 2: 180, 3: 200})
    assert hwm.modified_time > original_modified_time

    # update with equal value and multiple keys
    hwm.update({1: 100, 4: 300, 5: 400})
    assert hwm.value == frozendict({1: 100, 2: 180, 3: 200, 4: 300, 5: 400})

    hwm.update({6: 500, 2: 175})
    assert hwm.value == frozendict({1: 100, 2: 180, 3: 200, 4: 300, 5: 400, 6: 500})


def test_key_value_int_hwm_serialization():
    name = "key_value_int_hwm_name"
    modified_time = datetime.now() - timedelta(days=5)
    value = {"0": 100, "1": 123}

    hwm1 = KeyValueIntHWM(
        name=name,
        value=value,
        entity="topic_name",
        expression="some",
        description="some description",
        modified_time=modified_time,
    )

    expected1 = {
        "type": "key_value_int",
        "name": name,
        "value": value,
        "entity": "topic_name",
        "expression": "some",
        "description": "some description",
        "modified_time": modified_time.isoformat(),
    }

    serialized1 = hwm1.serialize()
    assert expected1 == serialized1
    assert KeyValueIntHWM.deserialize(serialized1) == hwm1

    hwm2 = KeyValueIntHWM(name=name, modified_time=modified_time)
    expected2 = {
        "type": "key_value_int",
        "name": name,
        "value": {},
        "entity": None,
        "expression": None,
        "description": "",
        "modified_time": modified_time.isoformat(),
    }

    serialized2 = hwm2.serialize()
    assert serialized2 == expected2
    assert KeyValueIntHWM.deserialize(serialized2) == hwm2
