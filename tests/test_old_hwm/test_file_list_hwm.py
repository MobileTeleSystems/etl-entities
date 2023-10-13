from datetime import datetime, timedelta
from pathlib import PosixPath

import pytest

from etl_entities.instance import AbsolutePath, RelativePath
from etl_entities.old_hwm import FileListHWM
from etl_entities.process import Process
from etl_entities.source import RemoteFolder


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
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")
    modified_time = datetime.now() - timedelta(days=5)

    full_name = f"file_list#{folder.name}"

    hwm1 = FileListHWM(source=folder)
    assert hwm1.source == folder
    assert hwm1.name == "file_list"
    assert hwm1.process is not None
    assert not hwm1.value
    assert not hwm1  # same as above

    assert str(hwm1) == full_name

    hwm2 = FileListHWM(source=folder, process=process)
    assert hwm2.source == folder
    assert hwm2.name == "file_list"
    assert hwm2.process == process
    assert not hwm2.value
    assert not hwm2  # same as above

    assert str(hwm2) == full_name

    hwm3 = FileListHWM(source=folder, value=[input_file])
    assert hwm3.source == folder
    assert hwm3.name == "file_list"
    assert hwm3.process is not None

    assert str(hwm3) == full_name

    assert result_file in hwm3.value
    assert hwm3

    hwm4 = FileListHWM(source=folder, value=input_file)
    assert hwm4.source == folder
    assert hwm4.name == "file_list"
    assert hwm4.process is not None
    assert result_file in hwm4.value
    assert hwm4

    assert str(hwm4) == full_name

    hwm5 = FileListHWM(source=folder, value=[input_file], process=process)
    assert hwm5.source == folder
    assert hwm5.name == "file_list"
    assert hwm5.process == process

    assert str(hwm5) == full_name

    assert result_file in hwm5.value
    assert hwm5

    hwm6 = FileListHWM(source=folder, value=[input_file], process=process, modified_time=modified_time)
    assert hwm6.source == folder
    assert hwm6.name == "file_list"
    assert hwm6.process == process
    assert hwm6.modified_time == modified_time

    assert str(hwm6) == full_name

    assert result_file in hwm6.value
    assert hwm6


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
    valid_file2 = RelativePath("another.csv")
    valid_value = [valid_file1, valid_file2]
    invalid_value = valid_value + [invalid_file]
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")

    with pytest.raises(ValueError):
        FileListHWM()

    with pytest.raises(ValueError):
        FileListHWM(value=valid_value)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=1)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=None)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=FileListHWM)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=valid_value, process=1)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=invalid_value, process=process)

    with pytest.raises(ValueError):
        FileListHWM(source=folder, value=valid_value, process=process, modified_time="unknown")

    if invalid_file != "":
        with pytest.raises(ValueError):
            FileListHWM(source=folder, value=invalid_file, process=process)


def test_file_list_hwm_set_value():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/test.csv")
    value = [file1, file2, file2, file3]
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm = FileListHWM(source=folder)

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
    hwm5.set_value(hwm1)
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
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")
    modified_time = datetime.now() - timedelta(days=5)

    hwm = FileListHWM(source=folder)

    for attr in ("value", "source", "process", "modified_time"):
        for item in (1, "abc", None, folder, process, file1, file2, file3, value, modified_time):
            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_file_list_hwm_compare():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("another.csv")

    value1 = [file1, file2]
    value2 = [file1, file2, file2]
    value3 = [file2, file3]

    folder1 = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    folder2 = RemoteFolder(name=AbsolutePath("/home/user/cde"), instance="ftp://my.domain:32")

    hwm = FileListHWM(source=folder1, value=value1)
    hwm_with_doubles = FileListHWM(source=folder1, value=value2)

    # modified_time is ignored while comparing HWMs
    modified_time = datetime.now() - timedelta(days=5)
    hwm1 = FileListHWM(source=folder1, value=value1, modified_time=modified_time)
    hwm2 = FileListHWM(source=folder2, value=value1)
    hwm3 = FileListHWM(source=folder1, value=value3)
    hwm4 = FileListHWM(source=folder2, value=value3)

    assert hwm == hwm1
    assert hwm == hwm_with_doubles

    items = (hwm1, hwm2, hwm3, hwm4)
    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_file_list_hwm_covers():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.csv")

    file4 = "another/path.py"
    file5 = RelativePath("test.csv")
    file6 = AbsolutePath("/home/user/abc/test.csv")

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    empty_hwm = FileListHWM(source=folder)

    assert not empty_hwm.covers(file1)
    assert not empty_hwm.covers(file2)
    assert not empty_hwm.covers(file3)
    assert not empty_hwm.covers(file4)
    assert not empty_hwm.covers(file5)
    assert not empty_hwm.covers(file6)

    hwm = FileListHWM(source=folder, value=[file1, file2, file3])

    assert hwm.covers(file1)
    assert hwm.covers(file2)
    assert hwm.covers(file3)
    assert not hwm.covers(file4)
    assert not hwm.covers(file5)
    assert not hwm.covers(file6)


def test_file_list_hwm_add():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=value1)
    hwm2 = FileListHWM(source=folder, value=value2)

    # empty value -> do nothing
    old_hwm = hwm1.copy()
    hwm3 = old_hwm + []
    hwm4 = old_hwm + {}

    assert hwm3 == hwm1
    assert hwm3.value == hwm1.value  # value is the same
    assert hwm3 is old_hwm  # nothing is changed, original object is returned
    assert hwm3.modified_time == hwm1.modified_time

    assert hwm4 == hwm1
    assert hwm4.value == hwm1.value  # value is the same
    assert hwm4 is old_hwm  # nothing is changed, original object is returned
    assert hwm4.modified_time == hwm1.modified_time

    # value already known -> do nothing
    old_hwm = hwm1.copy()
    hwm5 = old_hwm + file1
    hwm6 = old_hwm + [file1]
    hwm7 = old_hwm + {file1}

    assert hwm5 == hwm1
    assert hwm5.value == hwm1.value  # value is the same
    assert hwm5 is old_hwm  # nothing is changed, original object is returned
    assert hwm5.modified_time == hwm1.modified_time

    assert hwm6 == hwm1
    assert hwm6.value == hwm1.value  # value is the same
    assert hwm6 is old_hwm  # nothing is changed, original object is returned
    assert hwm6.modified_time == hwm1.modified_time

    assert hwm7 == hwm1
    assert hwm7.value == hwm1.value  # value is the same
    assert hwm7 is old_hwm  # nothing is changed, original object is returned
    assert hwm7.modified_time == hwm1.modified_time

    # if something has been changed, update modified_time
    old_hwm = hwm1.copy()
    hwm8 = old_hwm + file3
    hwm9 = old_hwm + [file3]
    hwm10 = old_hwm + {file3}

    assert hwm8 == hwm2
    assert hwm8.value == hwm2.value  # value is the updated
    assert hwm8 is not old_hwm  # a copy is returned
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm2
    assert hwm9.value == hwm2.value  # value is the updated
    assert hwm9 is not old_hwm  # a copy is returned
    assert hwm9.modified_time > hwm2.modified_time

    assert hwm10 == hwm2
    assert hwm10.value == hwm2.value  # value is the updated
    assert hwm10 is not old_hwm  # a copy is returned
    assert hwm10.modified_time > hwm2.modified_time

    old_hwm1 = hwm1.copy()
    old_hwm2 = hwm2.copy()

    hwm11 = old_hwm1 + hwm2
    hwm12 = old_hwm2 + hwm1

    assert hwm11 == hwm2
    assert hwm11.value == hwm2.value  # value is changed
    assert hwm11 is not old_hwm1  # a copy is returned
    assert hwm11.modified_time > hwm2.modified_time

    assert hwm12 == hwm2
    assert hwm12.value == hwm2.value  # value is the same
    assert hwm12 is old_hwm2  # nothing is changed, original object is returned
    assert hwm12.modified_time == hwm2.modified_time


def test_file_list_hwm_sub():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")
    file4 = RelativePath("unknown.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=value1)
    hwm2 = FileListHWM(source=folder, value=value2)

    # empty value -> do nothing
    old_hwm = hwm2.copy()
    hwm3 = old_hwm - []
    hwm4 = old_hwm - {}

    assert hwm3 == hwm2
    assert hwm3 is old_hwm  # nothing is changed, original object is returned
    assert hwm3.modified_time == hwm2.modified_time

    assert hwm4 == hwm2
    assert hwm4 is old_hwm  # nothing is changed, original object is returned
    assert hwm4.modified_time == hwm2.modified_time

    # value is unknown -> do nothing
    old_hwm = hwm2.copy()
    hwm5 = old_hwm - file4
    hwm6 = old_hwm - [file4]
    hwm7 = old_hwm - {file4}

    assert hwm5 == hwm2
    assert hwm5 is old_hwm  # nothing is changed, original object is returned
    assert hwm5.modified_time == hwm2.modified_time

    assert hwm6 == hwm2
    assert hwm6 is old_hwm  # nothing is changed, original object is returned
    assert hwm6.modified_time == hwm2.modified_time

    assert hwm7 == hwm2
    assert hwm7 is old_hwm  # nothing is changed, original object is returned
    assert hwm7.modified_time == hwm2.modified_time

    # if something has been changed, update modified_time
    old_hwm = hwm2.copy()
    hwm8 = old_hwm - file3
    hwm9 = old_hwm - [file3]
    hwm10 = old_hwm - {file3}

    assert hwm8 == hwm1
    assert hwm8 is not old_hwm  # a copy is returned
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm1
    assert hwm9 is not old_hwm  # a copy is returned
    assert hwm9.modified_time > hwm2.modified_time

    assert hwm10 == hwm1
    assert hwm10 is not old_hwm  # a copy is returned
    assert hwm10.modified_time > hwm2.modified_time

    hwm11 = hwm2 - hwm1
    hwm12 = FileListHWM(source=folder, value=[file3])

    assert hwm11 == hwm12
    assert hwm11 is not old_hwm  # a copy is returned
    assert hwm11.modified_time > hwm2.modified_time


def test_file_list_hwm_contains():
    name = PosixPath("/home/user/abc")
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value = [file1, file2]
    folder = RemoteFolder(name=name, instance="ftp://my.domain:23")

    hwm = FileListHWM(source=folder, value=value)

    # relative path is checked
    assert file1 in hwm
    assert RelativePath(file1) in hwm
    assert PosixPath(file1) in hwm

    # as well as absolute
    assert name / file1 in hwm
    assert str(name / file1) in hwm

    assert file3 not in hwm

    with pytest.raises(TypeError):
        assert 1 not in hwm

    with pytest.raises(TypeError):
        assert None not in hwm

    with pytest.raises(TypeError):
        assert folder not in hwm


def test_file_list_hwm_update():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=value1)
    hwm2 = FileListHWM(source=folder, value=value2)

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
    hwm11 = old_hwm11.update(hwm2)

    assert hwm11 == hwm2
    assert hwm11.value == old_hwm11.value == hwm2.value  # old object is updated
    assert hwm11 is old_hwm11  # in-place replacement
    assert hwm11.modified_time > hwm2.modified_time


def test_file_list_hwm_iter():
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=["some/path/file.py", RelativePath("another.csv")])
    assert set(hwm1) == {RelativePath("some/path/file.py"), RelativePath("another.csv")}

    hwm2 = FileListHWM(source=folder)
    assert set(hwm2) == set()


def test_file_list_hwm_len():
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=["some/path/file.py", RelativePath("another.csv")])
    assert len(hwm1) == 2

    hwm2 = FileListHWM(source=folder)
    assert not len(hwm2)


@pytest.mark.parametrize(
    "process, process_qualified_name",
    [
        (Process(name="myprocess", host="myhost"), "myprocess@myhost"),
        (Process(name="myprocess", task="abc", dag="cde", host="myhost"), "cde.abc.myprocess@myhost"),
    ],
)
def test_file_list_hwm_qualified_name(process, process_qualified_name):
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm = FileListHWM(
        source=folder,
        process=process,
    )
    assert hwm.qualified_name == f"file_list#/home/user/abc@ftp://my.domain:23#{process_qualified_name}"


def test_file_list_hwm_serialization():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = AbsolutePath("/home/user/abc/some.orc")

    value = [file1, file2, file2, file3]
    serialized_value1 = ["another.csv", "some.orc", "some/path/file.py"]
    serialized_value2 = ["another.csv", "some.orc", "some/path/file.py", "another.csv"]
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="abc", host="somehost", task="sometask", dag="somedag")
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value1,
        "type": "file_list",
        "source": folder.serialize(),
        "process": process.serialize(),
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = FileListHWM(source=folder, value=value, process=process, modified_time=modified_time)

    assert hwm1.serialize() == serialized1
    assert FileListHWM.deserialize(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = serialized_value2
    assert FileListHWM.deserialize(serialized2) == hwm1

    serialized3 = serialized1.copy()
    serialized3["value"] = []
    hwm2 = FileListHWM(source=folder, process=process, modified_time=modified_time)

    assert hwm2.serialize() == serialized3
    assert FileListHWM.deserialize(serialized3) == hwm2

    for wrong_value in [FileListHWM, None, ""]:  # noqa: WPS335
        serialized4 = serialized1.copy()
        serialized4["value"] = wrong_value
        with pytest.raises((TypeError, ValueError)):
            FileListHWM.deserialize_value(serialized4)

    serialized5 = serialized1.copy()
    serialized5["type"] = "unknown"
    with pytest.raises(KeyError):
        FileListHWM.deserialize(serialized5)

    serialized6 = serialized1.copy()
    serialized6["type"] = "int"
    with pytest.raises(ValueError):
        FileListHWM.deserialize(serialized6)
