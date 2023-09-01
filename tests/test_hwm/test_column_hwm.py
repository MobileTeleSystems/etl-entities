from datetime import date, datetime, timedelta

import pytest

from etl_entities.hwm import DateHWM, DateTimeHWM, IntHWM
from etl_entities.process import Process
from etl_entities.source import Column, Table


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (DateHWM, date.today()),
        (DateTimeHWM, datetime.now()),
        (IntHWM, 1),
    ],
)
def test_column_hwm_valid_input(hwm_class, value):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    process = Process(name="myprocess", host="myhost")
    modified_time = datetime.now() - timedelta(days=5)

    full_name = f"{column.name}#{table.full_name}"

    hwm1 = hwm_class(column=column, source=table)
    assert hwm1.value is None
    assert not hwm1  # same as above
    assert hwm1.column == column
    assert hwm1.name == column.name
    assert hwm1.source == table
    assert hwm1.process is not None
    assert hwm1.modified_time < datetime.now()

    assert str(hwm1) == full_name

    hwm2 = hwm_class(column=column, source=table, value=value)
    assert hwm2.value == value
    assert hwm2  # same as above
    assert hwm2.column == column
    assert hwm2.name == column.name
    assert hwm2.source == table
    assert hwm2.process is not None
    assert hwm2.modified_time < datetime.now()

    assert str(hwm2) == full_name

    hwm3 = hwm_class(column=column, source=table, process=process)
    assert hwm3.value is None
    assert not hwm3  # same as above
    assert hwm3.column == column
    assert hwm3.name == column.name
    assert hwm3.source == table
    assert hwm3.process == process
    assert hwm3.modified_time < datetime.now()

    assert str(hwm3) == full_name

    hwm4 = hwm_class(column=column, source=table, modified_time=modified_time)
    assert hwm4.value is None
    assert not hwm4  # same as above
    assert hwm4.column == column
    assert hwm4.name == column.name
    assert hwm4.source == table
    assert hwm4.modified_time == modified_time

    assert str(hwm4) == full_name

    hwm5 = hwm_class(column=column, source=table, value=value, process=process, modified_time=modified_time)
    assert hwm5.value == value
    assert hwm5  # same as above
    assert hwm5.column == column
    assert hwm5.name == column.name
    assert hwm5.source == table
    assert hwm5.process == process
    assert hwm5.modified_time == modified_time

    assert str(hwm5) == full_name


@pytest.mark.parametrize(
    "hwm_class, value, wrong_values",
    [
        (DateHWM, date.today(), ["1.1", "1", "2021-01-01T11:22:33", DateHWM]),
        (DateTimeHWM, datetime.now(), ["1.1", "1", DateTimeHWM]),
        (IntHWM, 1, [1.1, "1.1", IntHWM]),
    ],
)
def test_column_hwm_wrong_input(hwm_class, value, wrong_values):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")

    with pytest.raises(ValueError):
        hwm_class()

    with pytest.raises(ValueError):
        hwm_class(column=1)

    with pytest.raises(ValueError):
        hwm_class(source=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, source=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, source=table, value="abc")

    with pytest.raises(ValueError):
        hwm_class(column=column, source=table, value=[])

    for wrong_value in wrong_values:
        with pytest.raises(ValueError):
            hwm_class(column=column, source=table, value=wrong_value)

    with pytest.raises(ValueError):
        hwm_class(column=column, source=table, process=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, source=table, value=value, process=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, source=table, value=value, modified_time="unknown")


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (DateHWM, date.today()),
        (DateTimeHWM, datetime.now()),
        (IntHWM, 1),
    ],
)
def test_column_hwm_set_value(hwm_class, value):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    hwm = hwm_class(column=column, source=table)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert hwm1.value == value
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm1.copy()
    hwm2.set_value(None)
    assert hwm2.value is None
    assert hwm2.modified_time > hwm.modified_time

    with pytest.raises((TypeError, ValueError)):
        hwm.set_value("unknown")

    with pytest.raises(ValueError):
        hwm.set_value(column)

    with pytest.raises(ValueError):
        hwm.set_value(hwm1)


@pytest.mark.parametrize(
    "hwm_class",
    [
        DateHWM,
        DateTimeHWM,
        IntHWM,
    ],
)
def test_column_hwm_frozen(hwm_class):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    hwm = hwm_class(column=column, source=table)
    process = Process(name="myprocess", host="myhost")
    modified_time = datetime.now() - timedelta(days=5)

    for attr in ("value", "column", "source", "process", "modified_time"):
        for value in (1, "abc", date.today(), datetime.now(), None, column, table, process, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, value)


@pytest.mark.parametrize(  # noqa: WPS210
    "hwm_class, value, delta",
    [
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 1, 2),
    ],
)
def test_column_hwm_compare(hwm_class, value, delta):  # noqa: WPS210
    column1 = Column(name="some1")
    column2 = Column(name="some2")

    table1 = Table(name="abc.another1", instance="proto1://url1")
    table2 = Table(name="bcd.another2", instance="proto1://url2")

    hwm = hwm_class(column=column1, source=table1, value=value)

    # modified_time is ignored while comparing HWMs
    modified_time = datetime.now() - timedelta(days=5)
    hwm1 = hwm_class(column=column1, source=table1, value=value, modified_time=modified_time)
    hwm2 = hwm_class(column=column2, source=table1, value=value)
    hwm3 = hwm_class(column=column1, source=table2, value=value)
    hwm4 = hwm_class(column=column2, source=table2, value=value)

    next_value = value + delta

    hwm5 = hwm_class(column=column1, source=table1, value=next_value)
    hwm6 = hwm_class(column=column2, source=table1, value=next_value)
    hwm7 = hwm_class(column=column1, source=table2, value=next_value)
    hwm8 = hwm_class(column=column2, source=table2, value=next_value)

    items = (hwm1, hwm2, hwm3, hwm4)
    next_items = (hwm5, hwm6, hwm7, hwm8)
    valid_pairs = list(zip(items, next_items))

    assert hwm == hwm1

    for item in items:
        assert item == value
        assert item != next_value
        assert item < next_value

    for item in next_items:
        assert item == next_value
        assert item != value
        assert item > value

    for item1, item2 in valid_pairs:
        assert item1 < item2
        assert item2 > item1

    for item1 in items + next_items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2

                if (item1, item2) not in valid_pairs and (item2, item1) not in valid_pairs:
                    with pytest.raises(NotImplementedError):
                        assert item1 > item2

                    with pytest.raises(NotImplementedError):
                        assert item2 < item1


@pytest.mark.parametrize(  # noqa: WPS210
    "hwm_class, value, delta",
    [
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 1, 2),
    ],
)
def test_column_hwm_covers(hwm_class, value, delta):  # noqa: WPS210
    column = Column(name="some1")
    table = Table(name="abc.another1", instance="proto1://url1")

    empty_hwm = hwm_class(column=column, source=table)

    assert not empty_hwm.covers(value)
    assert not empty_hwm.covers(value - delta)
    assert not empty_hwm.covers(value + delta)

    hwm = hwm_class(column=column, source=table, value=value)

    assert hwm.covers(value)
    assert hwm.covers(value - delta)
    assert not hwm.covers(value + delta)


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (DateHWM, date.today()),
        (DateTimeHWM, datetime.now()),
        (IntHWM, 1),
    ],
)
def test_column_hwm_compare_other_type(hwm_class, value):  # noqa: WPS210
    other_types = {DateHWM, DateTimeHWM, IntHWM} - {hwm_class}

    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")

    hwm = hwm_class(column=column, source=table, value=value)

    for other_type in other_types:
        other_hwm = other_type(column=column, source=table)

        assert hwm != other_hwm

        with pytest.raises(TypeError):
            assert hwm > other_hwm

        with pytest.raises(TypeError):
            assert hwm < other_hwm


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 1, 2),
    ],
)
def test_column_hwm_add(hwm_class, value, delta):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    hwm = hwm_class(column=column, source=table)

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
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 1, 2),
    ],
)
def test_column_hwm_sub(hwm_class, value, delta):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    hwm = hwm_class(column=column, source=table)

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
    "hwm_class, value, delta",
    [
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 2, 1),
    ],
)
def test_column_hwm_update(hwm_class, value, delta):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    empty_hwm = hwm_class(column=column, source=table)

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
    hwm5 = hwm1.copy().copy(update={"value": value + delta})

    old_hwm6 = hwm1.copy()
    hwm6 = old_hwm6.update(value + delta)

    assert hwm6 == hwm5
    assert hwm6.value == old_hwm6.value == value + delta  # old object is updated
    assert hwm6 is old_hwm6  # in-place replacement
    assert hwm6.modified_time > hwm5.modified_time

    # cannot reset value to None, use `set_value` instead
    with pytest.raises(TypeError):
        _ = hwm1.update(None)

    if hwm_class != IntHWM:
        # cannot compare value with delta
        with pytest.raises(ValueError):
            _ = hwm.update(delta)

        with pytest.raises(TypeError):
            _ = hwm1.update(delta)


@pytest.mark.parametrize(
    "hwm_class",
    [
        DateHWM,
        DateTimeHWM,
        IntHWM,
    ],
)
@pytest.mark.parametrize(
    "column, column_qualified_name",
    [
        (Column(name="id", partition={"partition": "abc", "another": "cde"}), "id|partition=abc/another=cde"),
        (Column(name="id"), "id"),
    ],
)
@pytest.mark.parametrize(
    "table, table_qualified_name",
    [
        (
            Table(name="mydb.mytable", instance="dbtype://host.name:1234/schema"),
            "mydb.mytable@dbtype://host.name:1234/schema",
        ),
        (Table(name="mydb.mytable", instance="dbtype://host.name:1234"), "mydb.mytable@dbtype://host.name:1234"),
        (Table(name="mydb.mytable", instance="cluster"), "mydb.mytable@cluster"),
    ],
)
@pytest.mark.parametrize(
    "process, process_qualified_name",
    [
        (Process(name="myprocess", host="myhost"), "myprocess@myhost"),
        (Process(name="myprocess", task="abc", dag="cde", host="myhost"), "cde.abc.myprocess@myhost"),
    ],
)
def test_column_hwm_qualified_name(
    hwm_class,
    column,
    column_qualified_name,
    table,
    table_qualified_name,
    process,
    process_qualified_name,
):
    hwm = hwm_class(
        column=column,
        source=table,
        process=process,
    )
    assert hwm.qualified_name == f"{column_qualified_name}#{table_qualified_name}#{process_qualified_name}"


@pytest.mark.parametrize(
    "hwm_class, hwm_type, value, serialized_value, wrong_values",
    [
        (DateHWM, "date", date(year=2021, month=12, day=1), "2021-12-01", ["1", DateHWM, "unknown", []]),
        (
            DateTimeHWM,
            "datetime",
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
            ["1", DateTimeHWM, "unknown", []],
        ),
        (IntHWM, "int", 1, "1", ["1.0", IntHWM, "unknown", []]),
    ],
)
def test_column_hwm_serialization(hwm_class, hwm_type, value, serialized_value, wrong_values):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    process = Process(name="abc", host="somehost", task="sometask", dag="somedag")
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value,
        "type": hwm_type,
        "column": column.serialize(),
        "source": table.serialize(),
        "process": process.serialize(),
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = hwm_class(column=column, source=table, value=value, process=process, modified_time=modified_time)

    assert hwm1.serialize() == serialized1
    assert hwm_class.deserialize(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = "null"
    hwm2 = hwm_class(column=column, source=table, process=process, modified_time=modified_time)

    assert hwm2.serialize() == serialized2
    assert hwm_class.deserialize(serialized2) == hwm2

    for wrong_value in wrong_values + [None]:
        serialized3 = serialized1.copy()
        serialized3["value"] = wrong_value
        with pytest.raises((TypeError, ValueError)):
            hwm_class.deserialize_value(serialized3)

    serialized4 = serialized1.copy()
    serialized4["type"] = "unknown"
    with pytest.raises(KeyError):
        hwm_class.deserialize(serialized4)

    serialized5 = serialized1.copy()
    serialized5["type"] = "file_list"
    with pytest.raises(ValueError):
        hwm_class.deserialize(serialized5)
