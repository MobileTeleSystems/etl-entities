from datetime import datetime, timedelta

import pytest
from frozendict import frozendict

from etl_entities.hwm import KeyValueIntHWM


@pytest.mark.parametrize(
    "name, entity, expression, value, expected_value",
    [
        ("hwm_name", "topic_name", "offset", frozendict({0: 100, 1: 200}), frozendict({0: 100, 1: 200})),
        ("hwm_name", "topic_name", None, frozendict(), frozendict()),
    ],
)
def test_key_value_int_hwm_initialization(name, entity, expression, value, expected_value):
    modified_time = datetime.now() - timedelta(days=1)
    hwm = KeyValueIntHWM(name=name, entity=entity, expression=expression, value=value, modified_time=modified_time)
    assert hwm.name == name
    assert hwm.entity == entity
    assert hwm.expression == expression
    assert hwm.value == expected_value
    assert hwm.modified_time == modified_time
