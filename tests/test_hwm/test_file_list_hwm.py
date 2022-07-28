from datetime import datetime, timedelta
from pathlib import PosixPath

import pytest

from etl_entities.hwm import FileListHWM
from etl_entities.instance import AbsolutePath, RelativePath
from etl_entities.process import Process
from etl_entities.source import RemoteFolder


@pytest.mark.parametrize(
    "valid_files",
    [
        ("some", RelativePath("some"), RelativePath("some.file")),
        ("some/path", RelativePath("some/path"), RelativePath("some/folder/file.name")),
    ],
)
def test_file_list_hwm_valid_input(valid_files):
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

    hwm3 = FileListHWM(source=folder, value=valid_files)
    assert hwm3.source == folder
    assert hwm3.name == "file_list"
    assert hwm3.process is not None

    assert str(hwm3) == full_name

    for file in valid_files:
        assert RelativePath(file) in hwm3.value
    assert hwm3

    for file in valid_files:
        hwm4 = FileListHWM(source=folder, value=file)
        assert hwm4.source == folder
        assert hwm4.name == "file_list"
        assert hwm4.process is not None
        assert RelativePath(file) in hwm4.value
        assert hwm4

        assert str(hwm4) == full_name

    hwm5 = FileListHWM(source=folder, value=valid_files, process=process)
    assert hwm5.source == folder
    assert hwm5.name == "file_list"
    assert hwm5.process == process

    assert str(hwm5) == full_name

    for file in valid_files:
        assert RelativePath(file) in hwm5.value
    assert hwm5

    hwm6 = FileListHWM(source=folder, value=valid_files, process=process, modified_time=modified_time)
    assert hwm6.source == folder
    assert hwm6.name == "file_list"
    assert hwm6.process == process
    assert hwm6.modified_time == modified_time

    assert str(hwm6) == full_name

    for file in valid_files:
        assert RelativePath(file) in hwm6.value
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
        "/absolute",
        "/absolute.file",
        "/absolute.source/some.csv",
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


def test_file_list_hwm_with_value():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    value = [file1, file2, file2]
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm = FileListHWM(source=folder)

    hwm1 = hwm.with_value(value)
    assert RelativePath(file1) in hwm1
    assert file2 in hwm1
    assert hwm1.modified_time > hwm.modified_time

    hwm2 = hwm.with_value(file1)
    assert file1 in hwm2
    assert file2 not in hwm2
    assert hwm2.modified_time > hwm1.modified_time

    hwm3 = hwm.with_value(file2)
    assert file1 not in hwm3
    assert file2 in hwm3
    assert hwm3.modified_time > hwm2.modified_time

    with pytest.raises(ValueError):
        hwm.with_value("/absolute/path")

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(folder)

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(hwm1)


def test_file_list_hwm_frozen():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    value = [file1, file2]
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")
    modified_time = datetime.now() - timedelta(days=5)

    hwm = FileListHWM(source=folder)

    for attr in ("value", "source", "process", "modified_time"):
        for item in (1, "abc", None, folder, process, file1, file2, value, modified_time):

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


def test_file_list_hwm_add():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=value1)
    hwm2 = FileListHWM(source=folder, value=value2)

    # If one side is empty then nothing to change, modified_time is the same
    hwm3 = hwm1 + []
    hwm4 = hwm1 + {}

    assert hwm3 == hwm1
    assert hwm3.modified_time == hwm1.modified_time

    assert hwm4 == hwm1
    assert hwm4.modified_time == hwm1.modified_time

    hwm4 = hwm1 + file1
    hwm5 = hwm1 + [file1]
    hwm6 = hwm1 + {file1}

    assert hwm4 == hwm1
    assert hwm4.modified_time == hwm1.modified_time

    assert hwm5 == hwm1
    assert hwm5.modified_time == hwm1.modified_time

    assert hwm6 == hwm1
    assert hwm6.modified_time == hwm1.modified_time

    hwm7 = hwm1 + file3
    hwm8 = hwm1 + [file3]
    hwm9 = hwm1 + {file3}

    # if something has been changed, update modified_time
    assert hwm7 == hwm2
    assert hwm7.modified_time > hwm2.modified_time

    assert hwm8 == hwm2
    assert hwm8.modified_time > hwm2.modified_time

    assert hwm9 == hwm2
    assert hwm9.modified_time > hwm2.modified_time

    with pytest.raises(TypeError):
        _ = hwm1 + hwm2


def test_file_list_hwm_sub():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")

    hwm1 = FileListHWM(source=folder, value=value1)
    hwm2 = FileListHWM(source=folder, value=value2)

    # sub is not supported

    with pytest.raises(TypeError):
        _ = hwm1 - file3

    with pytest.raises(TypeError):
        _ = hwm1 - [file3]

    with pytest.raises(TypeError):
        _ = hwm1 - {file3}

    with pytest.raises(TypeError):
        _ = hwm1 - (file3,)

    with pytest.raises(TypeError):
        _ = hwm1 - hwm2


def test_file_list_hwm_contains():
    name = PosixPath("/home/user/abc")
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("other.py")

    value = [file1, file2]
    folder = RemoteFolder(name=name, instance="ftp://my.domain:23")

    hwm = FileListHWM(source=folder, value=value)

    assert file1 in hwm
    assert RelativePath(file1) in hwm
    assert PosixPath(file1) in hwm
    assert name / file1 in hwm
    assert str(name / file1) in hwm

    assert file3 not in hwm

    with pytest.raises(TypeError):
        assert 1 not in hwm

    with pytest.raises(TypeError):
        assert None not in hwm

    with pytest.raises(TypeError):
        assert folder not in hwm


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

    value = [file1, file2, file2]
    serialized_value1 = f"{file2}\n{file1}"
    serialized_value2 = f"{file2}\n{file1}\n{file2}"
    folder = RemoteFolder(name="/home/user/abc", instance="ftp://my.domain:23")
    process = Process(name="abc", host="somehost", task="sometask", dag="somedag")
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value1,
        "type": "files_list",
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
    serialized3["value"] = ""
    hwm2 = FileListHWM(source=folder, process=process, modified_time=modified_time)

    assert hwm2.serialize() == serialized3
    assert FileListHWM.deserialize(serialized3) == hwm2

    for wrong_value in [FileListHWM, None, []]:  # noqa: WPS335
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
