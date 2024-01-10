import secrets
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    HWMTypeRegistry,
)


@pytest.mark.parametrize(
    "hwm_class, input_value, value",
    [
        (ColumnDateHWM, date(2023, 12, 30), date(2023, 12, 30)),
        (ColumnDateHWM, "2023-12-30", date(2023, 12, 30)),
        (
            ColumnDateTimeHWM,
            datetime(2023, 12, 30, 11, 22, 33, 555000),
            datetime(2023, 12, 30, 11, 22, 33, 555000),
        ),
        (
            ColumnDateTimeHWM,
            "2023-12-30T11:22:33.555",
            datetime(2023, 12, 30, 11, 22, 33, 555000),
        ),
        (ColumnIntHWM, 1, 1),
        (ColumnIntHWM, "1", 1),
        (ColumnIntHWM, Decimal("1"), 1),
        (ColumnIntHWM, 1.0, 1),
        (ColumnIntHWM, "1.0", 1),
        (ColumnIntHWM, Decimal("1.0"), 1),
    ],
)
def test_column_hwm_valid_input(hwm_class, input_value, value):
    hwm_minimal = hwm_class(name="test", value=input_value)

    assert hwm_minimal.name == "test"
    assert hwm_minimal.value == value
    assert hwm_minimal.description == ""
    assert hwm_minimal.entity is None
    assert hwm_minimal.expression is None
    assert hwm_minimal.modified_time is not None

    mtime = datetime.now() - timedelta(days=5)
    hwm = hwm_class(
        name="test",
        description="my hwm",
        value=input_value,
        source="table",
        expression="CAST(column as TYPE)",
        modified_time=mtime,
    )

    assert hwm.name == "test"
    assert hwm.value == value
    assert hwm.description == "my hwm"
    assert hwm.entity == "table"
    assert hwm.expression == "CAST(column as TYPE)"
    assert hwm.modified_time == mtime


@pytest.mark.parametrize(
    "hwm_class, value, wrong_values",
    [
        (ColumnDateHWM, date.today(), ["abc", "1.1", "1", "2021-01-01T11:22:33", 1111, [], ColumnDateHWM]),
        (ColumnDateTimeHWM, datetime.now(), ["abc", "1.1", "1", 1111, [], ColumnDateTimeHWM]),
        (ColumnIntHWM, 1, ["1.23", Decimal("1.23"), "abc", [], ColumnIntHWM]),
    ],
)
def test_column_hwm_wrong_input(hwm_class, value, wrong_values):
    name = secrets.token_hex(8)

    with pytest.raises(ValueError):
        # missing name
        hwm_class()

    with pytest.raises(ValueError):
        # missing name
        hwm_class(source=1)

    for wrong_value in wrong_values:
        with pytest.raises(ValueError):
            hwm_class(name=name, value=wrong_value)

    with pytest.raises(ValueError):
        hwm_class(name=name, value=value, modified_time="unknown")

    with pytest.raises(ValueError):
        # extra fields not allowed
        hwm_class(name=name, unknown="unknown")


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (ColumnDateHWM, date.today()),
        (ColumnDateTimeHWM, datetime.now()),
        (ColumnIntHWM, 1),
    ],
)
def test_column_hwm_set_value(hwm_class, value):
    name = secrets.token_hex(8)
    hwm = hwm_class(name=name)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert hwm1.value == value
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm1.copy()
    hwm2.set_value(None)
    assert hwm2.value is None
    assert hwm2.modified_time > hwm.modified_time

    with pytest.raises((TypeError, ValueError)):
        hwm.set_value("invalid")

    with pytest.raises(ValueError):
        hwm.set_value(hwm1)


@pytest.mark.parametrize(
    "hwm_class",
    [
        ColumnDateHWM,
        ColumnDateTimeHWM,
        ColumnIntHWM,
    ],
)
def test_column_hwm_frozen(hwm_class):
    name = secrets.token_hex(8)
    hwm = hwm_class(name=name)
    modified_time = datetime.now() - timedelta(days=5)

    for attr in ("value", "name", "description", "entity", "expression", "modified_time"):
        for value in (1, "abc", date.today(), datetime.now(), None, name, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, value)


@pytest.mark.parametrize(  # noqa: WPS210
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_compare(hwm_class, value, delta):  # noqa: WPS210
    entity1 = "column_name_1"
    entity2 = "column_name_2"

    name1 = secrets.token_hex(8)
    name2 = secrets.token_hex(8)

    hwm1 = hwm_class(source=entity1, name=name1, value=value)
    hwm2 = hwm_class(source=entity2, name=name1, value=value)
    hwm3 = hwm_class(source=entity1, name=name2, value=value)
    hwm4 = hwm_class(source=entity2, name=name2, value=value)

    next_value = value + delta

    hwm5 = hwm_class(source=entity1, name=name1, value=next_value)
    hwm6 = hwm_class(source=entity2, name=name1, value=next_value)
    hwm7 = hwm_class(source=entity1, name=name2, value=next_value)
    hwm8 = hwm_class(source=entity2, name=name2, value=next_value)

    hwm_without_source = hwm_class(name=name1, value=value)

    # modified_time is ignored while comparing HWMs
    assert hwm1 != hwm_without_source

    modified_time = datetime.now() - timedelta(days=5)
    hwm_with_different_mtime = hwm_class(source=entity1, name=name1, value=value, modified_time=modified_time)

    # modified_time is ignored while comparing HWMs
    assert hwm1 == hwm_with_different_mtime

    items = (hwm1, hwm2, hwm3, hwm4)
    next_items = (hwm5, hwm6, hwm7, hwm8)
    valid_pairs = list(zip(items, next_items))

    # items with different attribute values (except modified_time) are not equal
    for item1 in items + next_items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2

    # this was true until 2.1.x, but not anymore
    for item in items + next_items:
        assert item != item.value

        with pytest.raises(TypeError):
            assert item > item.value

        with pytest.raises(TypeError):
            assert item > item.value

    # items with same attribute values can be compared using < and >
    for item1, item2 in valid_pairs:
        assert item1 < item2
        assert item2 > item1

    for item1 in items + next_items:
        for item2 in items:
            # items with different attribute values (except value and modified_time) cannot be compared using < and >
            if item1 is not item2 and (item1, item2) not in valid_pairs and (item2, item1) not in valid_pairs:
                with pytest.raises(NotImplementedError):
                    assert item1 > item2

                with pytest.raises(NotImplementedError):
                    assert item2 < item1


@pytest.mark.parametrize(
    "hwm_class",
    [
        ColumnDateHWM,
        ColumnDateTimeHWM,
        ColumnIntHWM,
    ],
)
def test_column_hwm_compare_other_type(hwm_class):  # noqa: WPS210
    name = secrets.token_hex(8)
    other_types = {ColumnDateHWM, ColumnDateTimeHWM, ColumnIntHWM} - {hwm_class}
    table = "table_name"

    hwm = hwm_class(name=name)
    hwm_with_source = hwm_class(name=name, source=table)

    for other_type in other_types:
        # HWM of different types are never equal
        other_hwm = other_type(name=name)
        other_hwm_with_same_source = other_type(name=name, source=table)

        assert other_hwm != hwm
        assert other_hwm_with_same_source != hwm_with_source

        # and cannot be compared with > or <
        with pytest.raises(TypeError):
            assert hwm > other_hwm

        with pytest.raises(TypeError):
            assert hwm_with_source > other_hwm_with_same_source

        with pytest.raises(TypeError):
            assert hwm < other_hwm

        with pytest.raises(TypeError):
            assert hwm_with_source < other_hwm_with_same_source


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_add(hwm_class, value, delta):
    name = secrets.token_hex(8)
    hwm = hwm_class(name=name)

    # if something has been changed, update modified_time
    hwm1 = hwm.copy(update={"value": value})
    hwm2 = hwm.copy(update={"value": value + delta})

    hwm3 = hwm1 + delta

    assert hwm3 == hwm2
    assert hwm3.value == hwm2.value == value + delta
    assert hwm3 is not hwm1  # a copy is returned
    assert hwm3.modified_time > hwm.modified_time

    # not allowed
    with pytest.raises(TypeError):
        _ = hwm3 + None

    with pytest.raises(TypeError):
        _ = hwm + None

    with pytest.raises(TypeError):
        _ = hwm + delta


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 1, 2),
    ],
)
def test_column_hwm_sub(hwm_class, value, delta):
    name = secrets.token_hex(8)
    hwm = hwm_class(name=name)

    hwm1 = hwm.copy(update={"value": value})
    hwm2 = hwm.copy(update={"value": value - delta})
    hwm3 = hwm1 - delta

    assert hwm3 == hwm2
    assert hwm3.value == hwm2.value == value - delta
    assert hwm3 is not hwm1  # a copy is returned
    assert hwm3.modified_time > hwm.modified_time

    # not allowed
    with pytest.raises(TypeError):
        _ = hwm3 - None

    with pytest.raises(TypeError):
        _ = hwm - None

    with pytest.raises(TypeError):
        _ = hwm - delta


@pytest.mark.parametrize(
    "hwm_class, hwm_type, value, serialized_value",
    [
        (
            ColumnDateHWM,
            "column_date",
            date(year=2021, month=12, day=1),
            "2021-12-01",
        ),
        (
            ColumnDateTimeHWM,
            "column_datetime",
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
        ),
        (ColumnIntHWM, "column_int", 1, 1),
    ],
)
def test_column_hwm_serialization(hwm_class, hwm_type, value, serialized_value):
    name = secrets.token_hex()
    modified_time = datetime.now()
    entity = "table"
    expression = "column"
    description = "my hwm"

    serialized1 = {
        "type": hwm_type,
        "name": name,
        "value": serialized_value,
        "entity": entity,
        "expression": expression,
        "description": description,
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = hwm_class(
        name=name,
        value=value,
        source=entity,
        expression=expression,
        description=description,
        modified_time=modified_time,
    )

    assert hwm1.serialize() == serialized1
    assert hwm_class.deserialize(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = None
    serialized2["entity"] = None
    serialized2["expression"] = None
    serialized2["description"] = ""
    hwm2 = hwm_class(name=name, modified_time=modified_time)

    assert hwm2.serialize() == serialized2
    assert hwm_class.deserialize(serialized2) == hwm2

    serialized2["value"] = "null"
    assert hwm_class.deserialize(serialized2) == hwm2


@pytest.mark.parametrize(
    "hwm_class",
    [
        ColumnDateHWM,
        ColumnDateTimeHWM,
        ColumnIntHWM,
    ],
)
def test_column_hwm_unregistered_type(hwm_class):
    class UnregisteredHWM(hwm_class):
        pass  # noqa: WPS604

    err_msg = r"You should register <class \'.*'> class using @register_hwm_type decorator"

    with pytest.raises(KeyError, match=err_msg):
        HWMTypeRegistry.get_key(UnregisteredHWM)


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (ColumnDateHWM, date.today(), timedelta(days=2)),
        (ColumnDateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (ColumnIntHWM, 2, 1),
    ],
)
def test_column_hwm_update(hwm_class, value, delta):
    name = "some_hwm_name"
    empty_hwm = hwm_class(name=name)

    # if both new and current values are None, do nothing
    old_hwm = empty_hwm.copy()
    hwm = old_hwm.update(None)

    assert hwm == empty_hwm
    assert hwm is old_hwm  # existing object is returned
    assert hwm.value is None
    assert old_hwm.value is None
    assert hwm.modified_time == empty_hwm.modified_time

    # if current value is None, set new value
    hwm1 = empty_hwm.copy(update={"value": value})

    old_hwm2 = empty_hwm.copy()
    hwm2 = old_hwm2.update(value)

    assert hwm2 == hwm1
    assert hwm2.value == old_hwm2.value == value  # old object is updated
    assert hwm2 is old_hwm2  # in-place replacement
    assert hwm2.modified_time > hwm1.modified_time

    # if input value is less than or equal to current, do nothing
    old_hwm3 = hwm1.copy()
    hwm3 = old_hwm3.update(value - delta)

    old_hwm4 = hwm1.copy()
    hwm4 = old_hwm4.update(value)

    assert hwm4 == hwm3 == hwm1
    assert hwm4.value == old_hwm4.value == hwm3.value == old_hwm3.value == value  # old object is returned
    assert hwm3 is old_hwm3  # in-place replacement
    assert hwm4 is old_hwm4  # in-place replacement
    assert hwm4.modified_time == hwm3.modified_time == hwm1.modified_time

    # if current value is less than input, use input as a new value and update modified_time
    hwm5 = hwm1.copy(update={"value": value + delta})

    old_hwm6 = hwm1.copy()
    hwm6 = old_hwm6.update(value + delta)

    assert hwm6 == hwm5
    assert hwm6.value == old_hwm6.value == value + delta  # old object is updated
    assert hwm6 is old_hwm6  # in-place replacement
    assert hwm6.modified_time > hwm5.modified_time

    # cannot reset value to None, use `set_value` instead
    with pytest.raises(TypeError):
        _ = hwm1.update(None)

    if hwm_class != ColumnIntHWM:
        # cannot compare value with delta
        with pytest.raises(ValueError):
            _ = hwm.update(delta)

        with pytest.raises(TypeError):
            _ = hwm1.update(delta)
