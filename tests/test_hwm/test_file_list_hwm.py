from datetime import datetime, timedelta
from pathlib import PosixPath

import pytest

from etl_entities.hwm import FileListHWM
from etl_entities.instance import AbsolutePath, RelativePath


@pytest.mark.parametrize(
    "input_file, result_file",
    [
        ("some", RelativePath("some")),
        (PosixPath("some"), RelativePath("some")),
        (RelativePath("some"), RelativePath("some")),
        ("some.file", RelativePath("some.file")),
        (PosixPath("some.file"), RelativePath("some.file")),
        (RelativePath("some.file"), RelativePath("some.file")),
        ("some/path", RelativePath("some/path")),
        (PosixPath("some/path"), RelativePath("some/path")),
        (RelativePath("some/path"), RelativePath("some/path")),
        ("some/folder/file.name", RelativePath("some/folder/file.name")),
        (PosixPath("some/folder/file.name"), RelativePath("some/folder/file.name")),
        (RelativePath("some/folder/file.name"), RelativePath("some/folder/file.name")),
        ("/home/user/abc/some/path", RelativePath("some/path")),
        (PosixPath("/home/user/abc/some/path"), RelativePath("some/path")),
        (AbsolutePath("/home/user/abc/some/path"), RelativePath("some/path")),
        ("/home/user/abc/some/folder/file.name", RelativePath("some/folder/file.name")),
        (PosixPath("/home/user/abc/some/folder/file.name"), RelativePath("some/folder/file.name")),
        (AbsolutePath("/home/user/abc/some/folder/file.name"), RelativePath("some/folder/file.name")),
    ],
)
def test_file_list_hwm_valid_input(input_file, result_file):
    folder = AbsolutePath("/home/user/abc")
    name = "file_list"
    modified_time = datetime.now() - timedelta(days=5)

    hwm1 = FileListHWM(name=name, directory=folder)
    assert hwm1.entity == folder
    assert hwm1.name == name
    assert not hwm1.value

    hwm2 = FileListHWM(name=name, directory=folder, value={input_file})

    assert hwm2.entity == folder
    assert hwm2.name == name
    assert result_file in hwm2
    assert hwm2

    hwm3 = FileListHWM(name=name, directory=folder, value={input_file}, modified_time=modified_time)
    assert hwm3.entity == folder
    assert hwm3.name == name
    assert hwm3.modified_time == modified_time
    assert result_file in hwm3.value
    assert hwm3


@pytest.mark.parametrize(
    "invalid_file",
    [
        1,
        None,
        "",
        ".",
        "..",
        "../another",
        "~/another",
        "some.file/../another",
        "/absolute/not/matching/source",
    ],
)
def test_file_list_hwm_wrong_input(invalid_file):
    valid_file1 = "some/path/file.py"
    valid_file2 = "another.csv"
    valid_value = [valid_file1, valid_file2]
    name = "file_list"
    invalid_value = valid_value + [invalid_file]
    folder = AbsolutePath("/home/user/abc")
    with pytest.raises(ValueError):
        FileListHWM()

    with pytest.raises(ValueError):
        FileListHWM(name=name)

    with pytest.raises(ValueError):
        FileListHWM(name=name, value=valid_value)

    with pytest.raises(ValueError):
        FileListHWM(name=name, directory=folder, value=1)

    with pytest.raises(ValueError):
        FileListHWM(name=name, directory=folder, value=None)

    with pytest.raises(ValueError):
        FileListHWM(name=name, directory=folder, value=FileListHWM)

    with pytest.raises(ValueError):
        FileListHWM(name=name, directory=folder, value=invalid_value)

    with pytest.raises(ValueError):
        FileListHWM(name=name, directory=folder, value=valid_value, modified_time="unknown")

    if invalid_file != "":
        with pytest.raises(ValueError):
            FileListHWM(name=name, directory=folder, value=invalid_file)


def test_file_list_hwm_set_value():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/test.csv")
    value = [file1, file2, file2, file3]
    name = "file_list"
    folder = AbsolutePath("/home/user/abc")

    hwm = FileListHWM(name=name, directory=folder)

    hwm1 = hwm.copy()
    hwm1.set_value(value)
    assert RelativePath(file1) in hwm1
    assert file2 in hwm1
    assert file3 in hwm1
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm.copy()
    hwm2.set_value(file1)
    assert file1 in hwm2
    assert file2 not in hwm2
    assert file3 not in hwm2
    assert hwm2.modified_time > hwm.modified_time

    hwm3 = hwm.copy()
    hwm3.set_value(file2)
    assert file1 not in hwm3
    assert file2 in hwm3
    assert file3 not in hwm3
    assert hwm3.modified_time > hwm.modified_time

    hwm4 = hwm.copy()
    hwm4.set_value(file3)
    assert file1 not in hwm4
    assert file2 not in hwm4
    assert file3 in hwm4
    assert hwm4.modified_time > hwm.modified_time

    hwm5 = hwm.copy()
    hwm5.set_value(hwm1.value)
    assert RelativePath(file1) in hwm5
    assert file2 in hwm5
    assert file3 in hwm5
    assert hwm5.modified_time > hwm.modified_time

    with pytest.raises(ValueError):
        hwm.set_value("/absolute/path/not/matching/source")

    with pytest.raises(ValueError):
        hwm.set_value(folder)


def test_file_list_hwm_frozen():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.csv")
    value = [file1, file2, file3]
    name = "file_list"
    folder = AbsolutePath("/home/user/abc")
    modified_time = datetime.now() - timedelta(days=5)

    hwm = FileListHWM(name=name, directory=folder)

    for attr in ("value", "entity", "modified_time"):
        for item in (1, "abc", None, folder, file1, file2, file3, value, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_file_list_hwm_compare():
    name = "file_list"

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("another.csv")

    value1 = [file1, file2]
    value2 = [file1, file2, file2]
    value3 = [file2, file3]

    folder1 = AbsolutePath("/home/user/abc")
    folder2 = AbsolutePath("/home/user/cde")

    hwm = FileListHWM(name=name, directory=folder1, value=value1)
    hwm_with_doubles = FileListHWM(name=name, directory=folder1, value=value2)

    # modified_time is ignored while comparing HWMs
    modified_time = datetime.now() - timedelta(days=5)
    hwm1 = FileListHWM(name=name, directory=folder1, value=value1, modified_time=modified_time)
    hwm2 = FileListHWM(name=name, directory=folder2, value=value1)
    hwm3 = FileListHWM(name=name, directory=folder1, value=value3)
    hwm4 = FileListHWM(name=name, directory=folder2, value=value3)

    assert hwm == hwm1
    assert hwm == hwm_with_doubles

    items = (hwm1, hwm2, hwm3, hwm4)
    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_file_list_hwm_covers():
    name = "file_list"

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.csv")

    file4 = "another/path.py"
    file5 = RelativePath("test.csv")
    file6 = AbsolutePath("/home/user/abc/test.csv")

    folder = AbsolutePath("/home/user/abc")

    empty_hwm = FileListHWM(name=name, directory=folder)

    assert not empty_hwm.covers(file1)
    assert not empty_hwm.covers(file2)
    assert not empty_hwm.covers(file3)
    assert not empty_hwm.covers(file4)
    assert not empty_hwm.covers(file5)
    assert not empty_hwm.covers(file6)

    hwm = FileListHWM(name=name, directory=folder, value=[file1, file2, file3])

    assert hwm.covers(file1)
    assert hwm.covers(file2)
    assert hwm.covers(file3)
    assert not hwm.covers(file4)
    assert not hwm.covers(file5)
    assert not hwm.covers(file6)


def test_file_list_hwm_add():
    name = "file_list"

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = AbsolutePath("/home/user/abc")

    hwm1 = FileListHWM(name=name, directory=folder, value=value1)
    hwm2 = FileListHWM(name=name, directory=folder, value=value2)

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

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")
    file4 = RelativePath("unknown.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = AbsolutePath("/home/user/abc")

    hwm1 = FileListHWM(name=name, directory=folder, value=value1)
    hwm2 = FileListHWM(name=name, directory=folder, value=value2)

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
    hwm5 = hwm - file4
    hwm6 = hwm - [file4]
    hwm7 = hwm - {file4}

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
    hwm8 = hwm - file3
    hwm9 = hwm - [file3]
    hwm10 = hwm - {file3}

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
    hwm12 = FileListHWM(name=name, directory=folder, value=[file3])

    assert hwm11 == hwm12
    assert hwm11 is not hwm  # a copy is returned
    assert hwm11.modified_time > hwm2.modified_time


def test_file_list_hwm_contains():
    name = "file_list"

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value = [file1, file2]
    folder = AbsolutePath("/home/user/abc")

    hwm = FileListHWM(name=name, directory=folder, value=value)

    # relative path is checked
    assert file1 in hwm
    assert RelativePath(file1) in hwm
    assert PosixPath(file1) in hwm

    # as well as absolute
    assert folder / file1 in hwm
    assert str(folder / file1) in hwm

    assert file3 not in hwm

    assert 1 not in hwm
    assert None not in hwm
    assert folder not in hwm


def test_file_list_hwm_update():
    name = "file_list"

    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = AbsolutePath("/home/user/abc")

    hwm1 = FileListHWM(name=name, directory=folder, value=value1)
    hwm2 = FileListHWM(name=name, directory=folder, value=value2)

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


def test_hwm_deserialize_value():
    remote_folder = AbsolutePath("/remote/folder")
    serialized_value = ["some/path.py", "/remote/folder/another/file"]

    deserialized_value = FileListHWM._deserialize_value(serialized_value, remote_folder)

    expected_value = frozenset(  # noqa: WPS527
        {
            RelativePath("some/path.py"),
            RelativePath("another/file"),
        },
    )  # This path is relative to remote_folder

    assert deserialized_value == expected_value


def test_file_list_hwm_serialization():
    name = "file_list"
    folder = AbsolutePath("/home/user/abc")
    modified_time = datetime.now() - timedelta(days=5)

    value = ["some/path/file.py"]

    hwm1 = FileListHWM(name=name, directory=folder, value=value, modified_time=modified_time)

    serialized1 = hwm1.serialize()

    expected = {
        "value": value,
        "type": "file_list",
        "directory": folder,
        "modified_time": modified_time.isoformat(),
        "name": name,
        "description": "",
        "expression": None,
    }

    assert expected == serialized1
    assert FileListHWM.deserialize(serialized1) == hwm1

    serialized2 = expected.copy()
    serialized2["value"] = []
    hwm2 = FileListHWM(name=name, directory=folder, modified_time=modified_time)

    assert hwm2.serialize() == serialized2
    assert FileListHWM.deserialize(serialized2) == hwm2
