from __future__ import annotations

import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

from etl_entities.hwm import FileModifiedTimeHWM
from etl_entities.instance import AbsolutePath


@pytest.mark.parametrize(
    "input_value, expected_value",
    [
        # values are always timezone-aware
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789),
            datetime(2023, 12, 30, 11, 22, 33, 456789).astimezone(),
        ),
        (
            "2023-12-30T11:22:33.456789",
            datetime(2023, 12, 30, 11, 22, 33, 456789).astimezone(),
        ),
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
        ),
        (
            "2023-12-30T11:22:33.456789+00:00",
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
        ),
        (
            1703935353.456789,  # timestampts are always UTC
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
        ),
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=3))),
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=3))),
        ),
        (
            "2023-12-30T11:22:33.456789+03:00",
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=3))),
        ),
    ],
)
def test_file_modified_time_hwm_valid_input(input_value, expected_value):
    name = "file_mtime"
    modified_time = datetime.now() - timedelta(days=5)

    empty_hwm = FileModifiedTimeHWM(name=name)
    assert empty_hwm.name == name
    assert empty_hwm.value is None

    minimal_hwm = FileModifiedTimeHWM(name=name, value=input_value)
    assert minimal_hwm.name == name
    assert minimal_hwm.value == expected_value

    hwm = FileModifiedTimeHWM(
        name=name,
        value=input_value,
        description="my hwm",
        directory="/absolute",
        expression="something",
        modified_time=modified_time,
    )
    assert hwm.name == name
    assert hwm.value == expected_value
    assert hwm.description == "my hwm"
    assert hwm.entity == AbsolutePath("/absolute")
    assert hwm.expression == "something"
    assert hwm.modified_time == modified_time


def test_file_modified_time_hwm_wrong_input():
    with pytest.raises(ValueError):
        # missing name
        FileModifiedTimeHWM()

    with pytest.raises(ValueError):
        # missing name
        FileModifiedTimeHWM(value=datetime(2025, 1, 1))

    with pytest.raises(ValueError):
        # cannot parse
        FileModifiedTimeHWM(name="file_mtime", value="wtf")

    with pytest.raises(ValueError):
        # extra fields not allowed
        FileModifiedTimeHWM(name="file_mtime", unknown="unknown")


@pytest.mark.parametrize(
    "input_value, expected_value",
    [
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789),
            datetime(2023, 12, 30, 11, 22, 33, 456789).astimezone(),
        ),
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone.utc),
        ),
        (
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=3))),
            datetime(2023, 12, 30, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=3))),
        ),
    ],
)
def test_file_modified_time_hwm_set_value(input_value, expected_value):
    hwm = FileModifiedTimeHWM(name="file_mtime")

    hwm1 = hwm.copy()
    hwm1.set_value(input_value)
    assert hwm1.value == expected_value
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm.copy()
    hwm2.set_value(input_value + timedelta(seconds=1))
    assert hwm2.value == expected_value + timedelta(seconds=1)
    assert hwm2.modified_time > hwm1.modified_time

    hwm3 = hwm2.copy()
    hwm3.set_value(input_value - timedelta(seconds=1))
    assert hwm3.value == expected_value - timedelta(seconds=1)
    assert hwm3.modified_time > hwm2.modified_time


def test_file_modified_time_hwm_frozen():
    hwm = FileModifiedTimeHWM(name="file_mtime")

    for attr in ("value", "entity", "expression", "description", "modified_time"):
        for item in (1, "abc", None, datetime.now()):
            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_file_modified_time_hwm_compare():
    name1 = secrets.token_hex()
    name2 = secrets.token_hex()

    value1 = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc)
    value2 = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone(timedelta(hours=1)))

    folder1 = AbsolutePath("/some/path")
    folder2 = AbsolutePath("/another/path")

    hwm1 = FileModifiedTimeHWM(name=name1, value=value1)
    hwm2 = FileModifiedTimeHWM(name=name2, value=value1)
    hwm3 = FileModifiedTimeHWM(name=name1, value=value2)
    hwm4 = FileModifiedTimeHWM(name=name2, value=value2)

    hwm5 = FileModifiedTimeHWM(name=name1, directory=folder1)
    hwm6 = FileModifiedTimeHWM(name=name1, directory=folder2)

    hwm7 = FileModifiedTimeHWM(name=name1, description="abc")
    hwm8 = FileModifiedTimeHWM(name=name1, description="bcd")

    hwm9 = FileModifiedTimeHWM(name=name1, expression="abc")
    hwm10 = FileModifiedTimeHWM(name=name1, expression="bcd")

    modified_time = datetime.now() - timedelta(days=5)
    hwm_with_different_mtime = FileModifiedTimeHWM(name=name1, value=value1, modified_time=modified_time)

    # modified time is ignored when comparing
    assert hwm1 == hwm_with_different_mtime

    items = (hwm1, hwm2, hwm3, hwm4, hwm5, hwm6, hwm7, hwm8, hwm9, hwm10)

    # items with different attribute values (except modified_time) are not equal
    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


@pytest.mark.parametrize(
    "tzinfo",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=3)),
    ],
)
def test_file_modified_time_hwm_covers(tzinfo):
    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=tzinfo)
    new_value = value + timedelta(seconds=1)

    empty_hwm = FileModifiedTimeHWM(name="file_mtime")
    assert not empty_hwm.covers(value)
    assert not empty_hwm.covers(new_value)

    hwm = FileModifiedTimeHWM(name="file_mtime", value=value)
    assert hwm.covers(value)
    assert not hwm.covers(new_value)

    assert hwm.covers(value.timestamp())
    assert not hwm.covers(new_value.timestamp())

    old_file = Mock(spec=Path)
    old_file_stat = Mock(spec=os.stat_result)
    old_file_stat.st_mtime = value.timestamp()
    old_file.stat.return_value = old_file_stat
    old_file.exists.return_value = True
    old_file.is_file.return_value = True

    new_file = Mock(spec=Path)
    new_file_stat = Mock(spec=os.stat_result)
    new_file_stat.st_mtime = new_value.timestamp()
    new_file.stat.return_value = new_file_stat
    new_file.exists.return_value = True
    new_file.is_file.return_value = True

    missing_path = Mock(spec=Path)
    missing_path.exists.return_value = False

    directory_path = Mock(spec=Path)
    directory_path.exists.return_value = True
    directory_path.is_file.return_value = False

    assert hwm.covers(old_file)
    assert not hwm.covers(new_file)
    assert not hwm.covers(missing_path)
    assert not hwm.covers(directory_path)


@pytest.mark.parametrize(
    "value",
    [
        datetime.now().astimezone(),
        None,
    ],
)
def test_file_modified_time_hwm_update_none(value):
    initial_hwm = FileModifiedTimeHWM(name="file_mtime", value=value)

    # empty value -> do nothing
    hwm = initial_hwm.copy()
    updated_hwm = hwm.update(None)
    updated_hwm = updated_hwm.update([])
    updated_hwm = updated_hwm.update({})

    assert updated_hwm.value == value  # unchanged
    assert updated_hwm == initial_hwm
    assert updated_hwm is hwm  # same obj is returned
    assert updated_hwm.modified_time == initial_hwm.modified_time


@pytest.mark.parametrize(
    "tzinfo",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=3)),
    ],
)
def test_file_modified_time_hwm_update_datetime(tzinfo: timezone | None):
    empty_hwm = FileModifiedTimeHWM(name="file_mtime")

    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=tzinfo)
    new_value = value + timedelta(seconds=1)

    hwm = empty_hwm.copy()
    updated_hwm = hwm.update(value)
    assert updated_hwm.value == value.astimezone()
    assert updated_hwm is hwm  # modified in-place
    assert hwm.modified_time > empty_hwm.modified_time
    latest_modified_time = hwm.modified_time

    updated_hwm = hwm.update(new_value)
    assert updated_hwm.value == new_value.astimezone()
    assert updated_hwm is hwm  # modified in-place
    assert updated_hwm.modified_time > latest_modified_time
    latest_modified_time = updated_hwm.modified_time

    updated_hwm = hwm.update(value)  # previous value
    assert updated_hwm.value == new_value.astimezone()  # unchanged
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time


@pytest.mark.parametrize(
    "tzinfo",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=3)),
    ],
)
def test_file_modified_time_hwm_update_timestamp(tzinfo: timezone | None):
    empty_hwm = FileModifiedTimeHWM(name="file_mtime")

    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=tzinfo)

    hwm = empty_hwm.copy()
    updated_hwm = hwm.update(value.timestamp())
    assert updated_hwm.value == value.astimezone()
    assert updated_hwm is hwm  # modified in-place
    assert hwm.modified_time > empty_hwm.modified_time
    latest_modified_time = hwm.modified_time

    updated_hwm = hwm.update(value.timestamp() + 1)
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)
    assert updated_hwm is hwm  # modified in-place
    assert updated_hwm.modified_time > latest_modified_time
    latest_modified_time = updated_hwm.modified_time

    updated_hwm = hwm.update(value.timestamp())  # previous value
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)  # unchanged
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time


@pytest.mark.parametrize(
    "tzinfo",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=3)),
    ],
)
def test_file_modified_time_hwm_update_filepath(tzinfo: timezone | None):
    empty_hwm = FileModifiedTimeHWM(name="file_mtime")

    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=tzinfo)

    old_file = Mock(spec=Path)
    old_file_stat = Mock(spec=os.stat_result)
    old_file_stat.st_mtime = value.timestamp()
    old_file.stat.return_value = old_file_stat
    old_file.exists.return_value = True
    old_file.is_file.return_value = True

    hwm = empty_hwm.copy()
    updated_hwm = hwm.update(old_file)
    assert updated_hwm.value == value.astimezone()
    assert updated_hwm is hwm  # modified in-place
    assert hwm.modified_time > empty_hwm.modified_time
    latest_modified_time = hwm.modified_time

    new_file = Mock(spec=Path)
    new_file_stat = Mock(spec=os.stat_result)
    new_file_stat.st_mtime = value.timestamp() + 1
    new_file.stat.return_value = new_file_stat
    new_file.exists.return_value = True
    new_file.is_file.return_value = True

    updated_hwm = hwm.update(new_file)
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)
    assert updated_hwm is hwm  # modified in-place
    assert updated_hwm.modified_time > latest_modified_time
    latest_modified_time = updated_hwm.modified_time

    updated_hwm = hwm.update(old_file)  # previous value
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)  # unchanged
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time

    missing_path = Mock(spec=Path)
    missing_path.exists.return_value = False

    updated_hwm = hwm.update(missing_path)
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time

    directory_path = Mock(spec=Path)
    directory_path.is_file.return_value = False

    updated_hwm = hwm.update(directory_path)
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time


@pytest.mark.parametrize(
    "tzinfo",
    [
        None,
        timezone.utc,
        timezone(timedelta(hours=3)),
    ],
)
def test_file_modified_time_hwm_update_filepath_iterable(tzinfo: timezone | None):
    empty_hwm = FileModifiedTimeHWM(name="file_mtime")

    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=tzinfo)

    old_file1 = Mock(spec=Path)
    old_file1_stat = Mock(spec=os.stat_result)
    old_file1_stat.st_mtime = value.timestamp() - 10
    old_file1.stat.return_value = old_file1_stat
    old_file1.exists.return_value = True
    old_file1.is_file.return_value = True

    old_file2 = Mock(spec=Path)
    old_file2_stat = Mock(spec=os.stat_result)
    old_file2_stat.st_mtime = value.timestamp()
    old_file2.stat.return_value = old_file2_stat
    old_file2.exists.return_value = True
    old_file2.is_file.return_value = True

    hwm = empty_hwm.copy()
    updated_hwm = hwm.update([old_file1, old_file2])
    assert updated_hwm.value == value.astimezone()
    assert updated_hwm is hwm  # modified in-place
    assert hwm.modified_time > empty_hwm.modified_time
    latest_modified_time = hwm.modified_time

    new_file = Mock(spec=Path)
    new_file_stat = Mock(spec=os.stat_result)
    new_file_stat.st_mtime = value.timestamp() + 1
    new_file.stat.return_value = new_file_stat
    new_file.exists.return_value = True
    new_file.is_file.return_value = True

    updated_hwm = hwm.update({new_file})
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)
    assert updated_hwm is hwm  # modified in-place
    assert updated_hwm.modified_time > latest_modified_time
    latest_modified_time = updated_hwm.modified_time

    updated_hwm = hwm.update([old_file1, new_file])  # previous value
    assert updated_hwm.value == value.astimezone() + timedelta(seconds=1)  # unchanged
    assert updated_hwm is hwm
    assert updated_hwm.modified_time == latest_modified_time


def test_file_modified_time_hwm_update_filepath_real(tmp_path: Path):
    non_existing = tmp_path / "missing"

    some_file = tmp_path / "new_file"
    some_file.touch()

    hwm = FileModifiedTimeHWM(name="file_mtime")
    assert not hwm.covers(some_file)
    assert not hwm.covers(tmp_path)
    assert not hwm.covers(non_existing)
    latest_modified_time = hwm.modified_time

    hwm.update(some_file)
    assert hwm.covers(some_file)
    assert not hwm.covers(tmp_path)
    assert not hwm.covers(non_existing)
    assert hwm.modified_time > latest_modified_time
    latest_modified_time = hwm.modified_time

    time.sleep(0.1)

    new_file = tmp_path / "new_file2"
    new_file.touch()

    assert not hwm.covers(new_file)
    assert not hwm.covers(tmp_path)
    assert not hwm.covers(non_existing)

    hwm.update([some_file, some_file.parent, non_existing, new_file])
    assert hwm.covers(some_file)
    assert hwm.covers(new_file)
    assert not hwm.covers(tmp_path)
    assert not hwm.covers(non_existing)
    assert hwm.modified_time > latest_modified_time
    latest_modified_time = hwm.modified_time

    hwm.update(some_file)
    assert hwm.covers(some_file)
    assert hwm.covers(new_file)
    assert not hwm.covers(tmp_path)
    assert not hwm.covers(non_existing)
    assert hwm.modified_time == latest_modified_time


def test_file_modified_time_hwm_serialization():
    modified_time = datetime.now() - timedelta(days=5)

    value = datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc)
    hwm = FileModifiedTimeHWM(
        name="file_mtime",
        value=value,
        directory="/some/path",
        expression="some",
        description="some description",
        modified_time=modified_time,
    )

    expected = {
        "type": "file_modification_time",
        "name": "file_mtime",
        "value": "2025-01-01T11:22:33.456789+00:00",
        "entity": "/some/path",
        "expression": "some",
        "description": "some description",
        "modified_time": modified_time.isoformat(),
    }

    serialized = hwm.serialize()
    assert expected == serialized
    assert FileModifiedTimeHWM.deserialize(serialized) == hwm

    empty_hwm = FileModifiedTimeHWM(name="file_mtime", modified_time=modified_time)
    empty_hwm_expected = {
        "type": "file_modification_time",
        "name": "file_mtime",
        "value": None,
        "entity": None,
        "expression": None,
        "description": "",
        "modified_time": modified_time.isoformat(),
    }

    empty_hwm_serialized = empty_hwm.serialize()
    assert empty_hwm_serialized == empty_hwm_expected
    assert FileModifiedTimeHWM.deserialize(empty_hwm_serialized) == empty_hwm
