import secrets
from datetime import datetime, timedelta
from pathlib import PosixPath, PurePosixPath

import pytest

from etl_entities.hwm import FileListHWM
from etl_entities.instance import AbsolutePath, RelativePath


@pytest.mark.parametrize(
    "input_file, result_file",
    [
        ("/absolute/path", AbsolutePath("/absolute/path")),
        (PurePosixPath("/absolute/path"), AbsolutePath("/absolute/path")),
        (PosixPath("/absolute/path"), AbsolutePath("/absolute/path")),
        (AbsolutePath("/absolute/path"), AbsolutePath("/absolute/path")),
    ],
)
def test_file_list_hwm_valid_input(input_file, result_file):
    name = "file_list"
    modified_time = datetime.now() - timedelta(days=5)

    empty_hwm = FileListHWM(name=name)
    assert empty_hwm.name == name
    assert empty_hwm.value == frozenset()

    minimal_hwm = FileListHWM(name=name, value=input_file)
    assert minimal_hwm.name == name
    assert minimal_hwm.value == frozenset((result_file,))

    hwm_with_duplicates = FileListHWM(name=name, value=[input_file, input_file])
    assert hwm_with_duplicates.name == name
    assert hwm_with_duplicates.value == frozenset((result_file,))

    hwm = FileListHWM(
        name=name,
        value={input_file},
        description="my hwm",
        directory="/absolute",
        expression="something",
        modified_time=modified_time,
    )
    assert hwm.name == name
    assert hwm.value == frozenset((result_file,))
    assert hwm.description == "my hwm"
    assert hwm.entity == AbsolutePath("/absolute")
    assert hwm.expression == "something"
    assert hwm.modified_time == modified_time


@pytest.mark.parametrize(
    "invalid_file",
    [
        "relative/path",
        "",
        ".",
        "..",
        "../another",
        "~/another",
        "some.file/../another",
        1,
        None,
    ],
)
def test_file_list_hwm_wrong_input(invalid_file):
    valid_file1 = "/some/path/file.py"
    valid_file2 = "/another.csv"
    valid_value = [valid_file1, valid_file2]

    name = "file_list"
    invalid_value = valid_value + [invalid_file]

    with pytest.raises(ValueError):
        # missing name
        FileListHWM()

    with pytest.raises(ValueError):
        # missing name
        FileListHWM(value=valid_value)

    with pytest.raises(ValueError):
        # relative path is not allowed as value
        FileListHWM(name=name, value=invalid_value)

    if invalid_file:
        with pytest.raises(ValueError):
            # relative path is not allowed as directory
            FileListHWM(name=name, directory=invalid_file)

    with pytest.raises(ValueError):
        # value does not match directory
        FileListHWM(name=name, value="/some/path/file.py", directory="/another/path")

    with pytest.raises(ValueError):
        # extra fields not allowed
        FileListHWM(name=name, unknown="unknown")


def test_file_list_hwm_set_value():
    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.csv")
    value = [file1, file2, file2, file3]
    name = "file_list"

    hwm = FileListHWM(name=name)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert hwm1.value == frozenset((AbsolutePath(file1), AbsolutePath(file2), AbsolutePath(file3)))
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm.copy()
    hwm2.set_value(file1)
    assert hwm2.value == frozenset((AbsolutePath(file1),))
    assert hwm2.modified_time > hwm.modified_time

    hwm3 = hwm.copy()
    hwm3.set_value(file2)
    assert hwm3.value == frozenset((AbsolutePath(file2),))
    assert hwm3.modified_time > hwm.modified_time

    hwm4 = hwm.copy()
    hwm4.set_value(file3)
    assert hwm4.value == frozenset((AbsolutePath(file3),))
    assert hwm4.modified_time > hwm.modified_time

    hwm5 = FileListHWM(name=name, directory="/some/path")
    hwm5.set_value(hwm1.value)
    assert hwm5.value == frozenset((AbsolutePath(file1), AbsolutePath(file2), AbsolutePath(file3)))
    assert hwm5.modified_time > hwm.modified_time

    with pytest.raises(ValueError):
        hwm.set_value("relative/path")

    with pytest.raises(ValueError):
        hwm_with_directory = FileListHWM(name=name, directory="/another/path")
        hwm_with_directory.set_value(file1)


def test_file_list_hwm_frozen():
    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.csv")
    value = [file1, file2, file3]
    name = "file_list"
    modified_time = datetime.now() - timedelta(days=5)

    hwm = FileListHWM(name=name)

    for attr in ("value", "entity", "expression", "description", "modified_time"):
        for item in (1, "abc", None, file1, file2, file3, value, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_file_list_hwm_compare():
    name1 = secrets.token_hex()
    name2 = secrets.token_hex()

    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/another.csv")

    value1 = [file1, file2]
    value3 = [file2, file3]

    folder1 = AbsolutePath("/some/path")
    folder2 = AbsolutePath("/another/path")

    hwm1 = FileListHWM(name=name1, value=value1)
    hwm2 = FileListHWM(name=name2, value=value1)
    hwm3 = FileListHWM(name=name1, value=value3)
    hwm4 = FileListHWM(name=name2, value=value3)

    hwm5 = FileListHWM(name=name1, directory=folder1)
    hwm6 = FileListHWM(name=name1, directory=folder2)

    hwm7 = FileListHWM(name=name1, description="abc")
    hwm8 = FileListHWM(name=name1, description="bcd")

    hwm9 = FileListHWM(name=name1, expression="abc")
    hwm10 = FileListHWM(name=name1, expression="bcd")

    modified_time = datetime.now() - timedelta(days=5)
    hwm_with_different_mtime = FileListHWM(name=name1, value=value1, modified_time=modified_time)

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


def test_file_list_hwm_covers():
    name = "file_list"

    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.orc")
    file4 = RelativePath("unknown.orc")

    empty_hwm = FileListHWM(name=name)

    assert not empty_hwm.covers(file1)
    assert not empty_hwm.covers(file2)
    assert not empty_hwm.covers(file3)
    assert not empty_hwm.covers(file4)

    hwm = FileListHWM(name=name, value=[file1, file2, file3])

    assert hwm.covers(file1)
    assert hwm.covers(file2)
    assert hwm.covers(file3)
    assert not hwm.covers(file4)


def test_file_list_hwm_add():
    name = "file_list"

    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    hwm1 = FileListHWM(name=name, value=value1)
    hwm2 = FileListHWM(name=name, value=value2)

    # empty value -> do nothing
    hwm = hwm1.copy()
    hwm3 = hwm + []
    hwm4 = hwm + {}

    assert hwm3 == hwm1
    assert hwm3.value == hwm1.value  # value is the same
    assert hwm3 is hwm  # nothing is changed, original object is returned
    assert hwm3.modified_time == hwm1.modified_time

    assert hwm4 == hwm1
    assert hwm4.value == hwm1.value  # value is the same
    assert hwm4 is hwm  # nothing is changed, original object is returned
    assert hwm4.modified_time == hwm1.modified_time

    # value already known -> do nothing
    hwm = hwm1.copy()
    hwm5 = hwm + file1
    hwm6 = hwm + [file1]
    hwm7 = hwm + {file1}

    assert hwm5 == hwm1
    assert hwm5.value == hwm1.value  # value is the same
    assert hwm5 is hwm  # nothing is changed, original object is returned
    assert hwm5.modified_time == hwm1.modified_time

    assert hwm6 == hwm1
    assert hwm6.value == hwm1.value  # value is the same
    assert hwm6 is hwm  # nothing is changed, original object is returned
    assert hwm6.modified_time == hwm1.modified_time

    assert hwm7 == hwm1
    assert hwm7.value == hwm1.value  # value is the same
    assert hwm7 is hwm  # nothing is changed, original object is returned
    assert hwm7.modified_time == hwm1.modified_time

    # if something has been changed, update modified_time
    hwm = hwm1.copy()
    hwm8 = hwm + file3
    hwm9 = hwm + [file3]
    hwm10 = hwm + {file3}

    assert hwm8 == hwm2
    assert hwm8.value == hwm2.value  # value is the updated
    assert hwm8 is not hwm  # a copy is returned
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm2
    assert hwm9.value == hwm2.value  # value is the updated
    assert hwm9 is not hwm  # a copy is returned
    assert hwm9.modified_time > hwm2.modified_time

    assert hwm10 == hwm2
    assert hwm10.value == hwm2.value  # value is the updated
    assert hwm10 is not hwm  # a copy is returned
    assert hwm10.modified_time > hwm2.modified_time

    hwm1 = hwm1.copy()
    hwm2 = hwm2.copy()

    hwm11 = hwm1 + hwm2.value
    hwm12 = hwm2 + hwm1.value

    assert hwm11 == hwm2
    assert hwm11.value == hwm2.value  # value is changed
    assert hwm11 is not hwm1  # a copy is returned
    assert hwm11.modified_time > hwm2.modified_time

    assert hwm12 == hwm2
    assert hwm12.value == hwm2.value  # value is the same
    assert hwm12 is hwm2  # nothing is changed, original object is returned
    assert hwm12.modified_time == hwm2.modified_time


def test_file_list_hwm_sub():
    name = "file_list"

    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.orc")

    value1 = [file1]
    value2 = [file1, file2]

    hwm1 = FileListHWM(name=name, value=value1)
    hwm2 = FileListHWM(name=name, value=value2)

    # empty value -> do nothing
    hwm = hwm2.copy()
    hwm3 = hwm - []
    hwm4 = hwm - {}

    assert hwm3 == hwm2
    assert hwm3 is hwm  # nothing is changed, original object is returned
    assert hwm3.modified_time == hwm2.modified_time

    assert hwm4 == hwm2
    assert hwm4 is hwm  # nothing is changed, original object is returned
    assert hwm4.modified_time == hwm2.modified_time

    # value is unknown -> do nothing
    hwm = hwm2.copy()
    hwm5 = hwm - file3
    hwm6 = hwm - [file3]
    hwm7 = hwm - {file3}

    assert hwm5 == hwm2
    assert hwm5 is hwm  # nothing is changed, original object is returned
    assert hwm5.modified_time == hwm2.modified_time

    assert hwm6 == hwm2
    assert hwm6 is hwm  # nothing is changed, original object is returned
    assert hwm6.modified_time == hwm2.modified_time

    assert hwm7 == hwm2
    assert hwm7 is hwm  # nothing is changed, original object is returned
    assert hwm7.modified_time == hwm2.modified_time

    # if something has been changed, update modified_time
    hwm = hwm2.copy()
    hwm8 = hwm - file2
    hwm9 = hwm - [file2]
    hwm10 = hwm - {file2}

    assert hwm8 == hwm1
    assert hwm8 is not hwm  # a copy is returned
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm1
    assert hwm9 is not hwm  # a copy is returned
    assert hwm9.modified_time > hwm2.modified_time

    assert hwm10 == hwm1
    assert hwm10 is not hwm  # a copy is returned
    assert hwm10.modified_time > hwm2.modified_time

    hwm11 = hwm2 - hwm1.value
    hwm12 = FileListHWM(name=name, value=[file2])

    assert hwm11 == hwm12
    assert hwm11 is not hwm  # a copy is returned
    assert hwm11.modified_time > hwm2.modified_time


def test_file_list_hwm_contains():
    name = "file_list"

    file1 = "/some/path/file.py"
    file2 = PurePosixPath("/some/path/file.txt")
    file3 = AbsolutePath("/some/path/file.orc")
    file4 = "unknown.orc"
    file5 = RelativePath("unknown.orc")

    empty_hwm = FileListHWM(name=name)

    assert file1 not in empty_hwm
    assert file2 not in empty_hwm
    assert file3 not in empty_hwm
    assert file4 not in empty_hwm
    assert file5 not in empty_hwm

    hwm = FileListHWM(name=name, value=[file1, file2])

    assert file1 in hwm
    assert file2 in hwm
    assert file3 not in hwm
    assert file4 not in hwm
    assert file5 not in hwm

    assert 1 not in hwm
    assert None not in hwm

    hwm_with_directory = FileListHWM(name=name, directory="/another/path")

    assert file1 not in hwm_with_directory
    assert file2 not in hwm_with_directory
    assert file3 not in hwm_with_directory
    assert file4 not in hwm_with_directory
    assert file5 not in hwm_with_directory


def test_file_list_hwm_update():
    name = "file_list"

    file1 = "/some/path/file.py"
    file2 = "/some/path/file.txt"
    file3 = AbsolutePath("/some/path/file.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    hwm1 = FileListHWM(name=name, value=value1)
    hwm2 = FileListHWM(name=name, value=value2)

    # empty value -> do nothing
    old_hwm3 = hwm1.copy()
    hwm3 = old_hwm3.update([])

    old_hwm4 = hwm1.copy()
    hwm4 = old_hwm4.update({})

    assert hwm3 == hwm1
    assert hwm3 is old_hwm3  # old object is returned
    assert hwm3.modified_time == hwm1.modified_time

    assert hwm4 == hwm1
    assert hwm4 is old_hwm4  # old object is returned
    assert hwm4.modified_time == hwm1.modified_time

    # value already known -> do nothing
    old_hwm5 = hwm1.copy()
    hwm5 = old_hwm5.update(file1)

    old_hwm6 = hwm1.copy()
    hwm6 = old_hwm6.update([file1])

    old_hwm7 = hwm1.copy()
    hwm7 = old_hwm7.update({file1})

    assert hwm5 == hwm1
    assert hwm5 is old_hwm5  # old object is returned
    assert hwm5.modified_time == hwm1.modified_time

    assert hwm6 == hwm1
    assert hwm6 is old_hwm6  # old object is returned
    assert hwm6.modified_time == hwm1.modified_time

    assert hwm7 == hwm1
    assert hwm7 is old_hwm7  # old object is returned
    assert hwm7.modified_time == hwm1.modified_time

    old_hwm8 = hwm1.copy()
    hwm8 = old_hwm8.update(file3)

    old_hwm9 = hwm1.copy()
    hwm9 = old_hwm9.update([file3])

    old_hwm10 = hwm1.copy()
    hwm10 = old_hwm10.update({file3})

    # if something has been changed, update modified_time
    assert hwm8 == hwm2
    assert hwm8.value == old_hwm8.value == hwm2.value  # old object is updated
    assert hwm8 is old_hwm8  # in-place replacement
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm2
    assert hwm9.value == old_hwm9.value == hwm2.value  # old object is updated
    assert hwm9 is old_hwm9  # in-place replacement
    assert hwm9.modified_time > hwm2.modified_time

    assert hwm10 == hwm2
    assert hwm10.value == old_hwm10.value == hwm2.value  # old object is updated
    assert hwm10 is old_hwm10  # in-place replacement
    assert hwm10.modified_time > hwm2.modified_time

    old_hwm11 = hwm1.copy()
    hwm11 = old_hwm11.update(hwm2.value)

    assert hwm11 == hwm2
    assert hwm11.value == old_hwm11.value == hwm2.value  # old object is updated
    assert hwm11 is old_hwm11  # in-place replacement
    assert hwm11.modified_time > hwm2.modified_time


def test_file_list_hwm_serialization():
    name = "file_list"
    modified_time = datetime.now() - timedelta(days=5)

    value = ["/some/path/file.py"]
    hwm1 = FileListHWM(
        name=name,
        value=value,
        directory="/some/path",
        expression="some",
        description="some description",
        modified_time=modified_time,
    )

    expected1 = {
        "type": "file_list",
        "name": name,
        "value": value,
        "entity": "/some/path",
        "expression": "some",
        "description": "some description",
        "modified_time": modified_time.isoformat(),
    }

    serialized1 = hwm1.serialize()
    assert expected1 == serialized1
    assert FileListHWM.deserialize(serialized1) == hwm1

    hwm2 = FileListHWM(name=name, modified_time=modified_time)
    expected2 = {
        "type": "file_list",
        "name": name,
        "value": [],
        "entity": None,
        "expression": None,
        "description": "",
        "modified_time": modified_time.isoformat(),
    }

    serialized2 = hwm2.serialize()
    assert serialized2 == expected2
    assert FileListHWM.deserialize(serialized2) == hwm2
