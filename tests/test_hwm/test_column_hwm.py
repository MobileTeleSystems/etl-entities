from datetime import date, datetime, timedelta

import pytest

from hwmlib.hwm import DateHWM, DateTimeHWM, IntHWM
from hwmlib.process import Process
from hwmlib.source import Column, Table


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
    table = Table(name="another", db="abc", instance="proto://url")
    process = Process(name="myprocess", host="myhost")

    hwm1 = hwm_class(column=column, table=table, value=value, process=process)
    assert hwm1.value == value
    assert hwm1  # same as above
    assert hwm1.column == column
    assert hwm1.name == column.name
    assert hwm1.table == table
    assert hwm1.process == process

    hwm2 = hwm_class(column=column, table=table, value=value)
    assert hwm2.value == value
    assert hwm2  # same as above
    assert hwm2.column == column
    assert hwm2.name == column.name
    assert hwm2.table == table
    assert hwm2.process is not None

    hwm3 = hwm_class(column=column, table=table, process=process)
    assert hwm3.value is None
    assert not hwm3  # same as above
    assert hwm3.column == column
    assert hwm3.name == column.name
    assert hwm3.table == table
    assert hwm3.process == process

    hwm4 = hwm_class(column=column, table=table)
    assert hwm4.value is None
    assert not hwm4  # same as above
    assert hwm4.column == column
    assert hwm4.name == column.name
    assert hwm4.table == table
    assert hwm4.process is not None


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (DateHWM, date.today()),
        (DateTimeHWM, datetime.now()),
        (IntHWM, 1),
    ],
)
def test_column_hwm_wrong_input(hwm_class, value):
    column = Column(name="some")
    table = Table(name="another", db="abc", instance="proto://url")

    with pytest.raises(ValueError):
        hwm_class()

    with pytest.raises(ValueError):
        hwm_class(column=1)

    with pytest.raises(ValueError):
        hwm_class(table=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, table=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, table=table, value="abc")

    with pytest.raises(ValueError):
        hwm_class(column=column, table=table, value=[])

    with pytest.raises(ValueError):
        hwm_class(column=column, table=table, process=1)

    with pytest.raises(ValueError):
        hwm_class(column=column, table=table, value=value, process=1)


@pytest.mark.parametrize(
    "hwm_class, value",
    [
        (DateHWM, date.today()),
        (DateTimeHWM, datetime.now()),
        (IntHWM, 1),
    ],
)
def test_column_hwm_with_value(hwm_class, value):
    column = Column(name="some")
    table = Table(name="another", db="abc", instance="proto://url")
    hwm = hwm_class(column=column, table=table)

    hwm1 = hwm.with_value(value)
    assert hwm1.value == value

    # None preserves original HWM value
    hwm2 = hwm1.with_value(None)
    assert hwm2.value == value

    with pytest.raises(ValueError):
        hwm.with_value("unknown")

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(column)

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(hwm1)


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
    table = Table(name="another", db="abc", instance="proto://url")
    hwm = hwm_class(column=column, table=table)
    process = Process(name="myprocess", host="myhost")

    for attr in ("value", "column", "table", "process"):
        for value in (1, "abc", date.today(), datetime.now(), None, column, table, process):

            with pytest.raises(TypeError):
                setattr(hwm, attr, value)


@pytest.mark.parametrize(
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

    table1 = Table(name="another1", db="abc", instance="proto1://url1")
    table2 = Table(name="another2", db="bcd", instance="proto1://url2")

    hwm = hwm_class(column=column1, table=table1, value=value)

    hwm1 = hwm_class(column=column1, table=table1, value=value)
    hwm2 = hwm_class(column=column2, table=table1, value=value)
    hwm3 = hwm_class(column=column1, table=table2, value=value)
    hwm4 = hwm_class(column=column2, table=table2, value=value)

    next_value = value + delta

    hwm5 = hwm_class(column=column1, table=table1, value=next_value)
    hwm6 = hwm_class(column=column2, table=table1, value=next_value)
    hwm7 = hwm_class(column=column1, table=table2, value=next_value)
    hwm8 = hwm_class(column=column2, table=table2, value=next_value)

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


@pytest.mark.parametrize(
    "hwm_class, value, delta",
    [
        (DateHWM, date.today(), timedelta(days=2)),
        (DateTimeHWM, datetime.now(), timedelta(seconds=2)),
        (IntHWM, 1, 2),
    ],
)
def test_column_hwm_compare_other_type(hwm_class, value, delta):  # noqa: WPS210
    other_types = {DateHWM, DateTimeHWM, IntHWM} - {hwm_class}

    column = Column(name="some")
    table = Table(name="another", db="abc", instance="proto://url")

    hwm = hwm_class(column=column, table=table, value=value)

    for other_type in other_types:
        other_hwm = other_type(column=column, table=table)

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
    table = Table(name="another", db="abc", instance="proto://url")
    hwm = hwm_class(column=column, table=table)

    hwm1 = hwm.with_value(value)
    hwm2 = hwm.with_value(value + delta)

    # If one side is none then nothing to change
    assert hwm + delta == hwm
    assert (hwm + None) == hwm

    assert hwm1 + delta == hwm2

    with pytest.raises(TypeError):
        _ = hwm1 + hwm2


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
    table = Table(name="another", db="abc", instance="proto://url")
    hwm = hwm_class(column=column, table=table)

    # If one side is none then nothing to change
    assert hwm - delta == hwm
    assert (hwm - None) == hwm

    hwm1 = hwm.with_value(value)
    hwm2 = hwm.with_value(value + delta)

    assert hwm2 - delta == hwm1

    with pytest.raises(TypeError):
        _ = hwm1 - hwm2


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
            Table(name="mytable", db="mydb", instance="dbtype://host.name:1234/schema"),
            "mydb.mytable@dbtype://host.name:1234/schema",
        ),
        (Table(name="mytable", db="mydb", instance="dbtype://host.name:1234"), "mydb.mytable@dbtype://host.name:1234"),
        (Table(name="mytable", db="mydb", instance="cluster"), "mydb.mytable@cluster"),
    ],
)
@pytest.mark.parametrize(
    "process, process_qualified_name",
    [
        (Process(name="myprocess", host="myhost"), "myprocess@myhost"),
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
    process = Process(name="myprocess", host="myhost")

    hwm = hwm_class(
        column=column,
        table=table,
        process=process,
    )
    assert hwm.qualified_name == f"{column_qualified_name}#{table_qualified_name}#{process_qualified_name}"


@pytest.mark.parametrize(
    "hwm_class, value, serialized",
    [
        (DateHWM, date(year=2021, month=12, day=1), "2021-12-01"),
        (DateTimeHWM, datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33), "2021-12-01T04:20:33"),
        (IntHWM, 1, "1"),
    ],
)
def test_column_hwm_serialize(hwm_class, value, serialized):
    column = Column(name="some")
    table = Table(name="another", db="abc", instance="proto://url")

    hwm1 = hwm_class(column=column, table=table, value=value)
    assert hwm1.serialize() == serialized

    hwm2 = hwm_class(column=column, table=table)
    assert hwm2.serialize() == "null"


@pytest.mark.parametrize(
    "hwm_class, value, serialized, wrong_values",
    [
        (DateHWM, date(year=2021, month=12, day=1), "2021-12-01", ["1", DateHWM, "unknown", []]),
        (
            DateTimeHWM,
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
            ["1", DateTimeHWM, "unknown", []],
        ),
        (IntHWM, 1, "1", ["1.0", IntHWM, "unknown", []]),
    ],
)
def test_column_hwm_deserialize(hwm_class, value, serialized, wrong_values):
    column = Column(name="some")
    table = Table(name="another", db="abc", instance="proto://url")

    assert hwm_class.deserialize(serialized) == value
    assert hwm_class.deserialize("null") is None

    assert hwm_class(column=column, table=table, value=serialized) == value
    assert not hwm_class(column=column, table=table, value="null")

    for wrong_value in wrong_values:
        with pytest.raises((TypeError, ValueError)):
            hwm_class(column=column, table=table, value=wrong_value)

    for wrong_value in wrong_values + [None]:
        with pytest.raises((TypeError, ValueError)):
            hwm_class.deserialize(wrong_value)
