from pathlib import PosixPath

import pytest

from etl_entities.hwm import FileListHWM
from etl_entities.location import AbsolutePath, RelativePath
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
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")

    hwm1 = FileListHWM(folder=folder, value=valid_files, process=process)

    assert hwm1.folder == folder
    assert hwm1.name == "downloaded_files"
    assert hwm1.process == process

    for file in valid_files:
        assert RelativePath(file) in hwm1.value
    assert hwm1

    hwm2 = FileListHWM(folder=folder, value=valid_files)
    assert hwm2.folder == folder
    assert hwm2.name == "downloaded_files"
    assert hwm2.process is not None

    for file in valid_files:
        assert RelativePath(file) in hwm2.value
    assert hwm2

    for file in valid_files:
        hwm3 = FileListHWM(folder=folder, value=file)
        assert hwm3.folder == folder
        assert hwm3.name == "downloaded_files"
        assert hwm3.process is not None
        assert RelativePath(file) in hwm3.value
        assert hwm3

    hwm4 = FileListHWM(folder=folder, process=process)
    assert hwm4.folder == folder
    assert hwm4.name == "downloaded_files"
    assert hwm4.process == process
    assert not hwm4.value
    assert not hwm4  # same as above

    hwm5 = FileListHWM(folder=folder)
    assert hwm5.folder == folder
    assert hwm5.name == "downloaded_files"
    assert hwm5.process is not None
    assert not hwm5.value
    assert not hwm5  # same as above


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
        "/absolute.folder/some.csv",
    ],
)
def test_file_list_hwm_wrong_input(invalid_file):
    valid_file1 = "some/path/file.py"
    valid_file2 = RelativePath("another.csv")
    valid_value = [valid_file1, valid_file2]
    invalid_value = valid_value + [invalid_file]
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")

    with pytest.raises(ValueError):
        FileListHWM()

    with pytest.raises(ValueError):
        FileListHWM(value=valid_value)

    with pytest.raises(ValueError):
        FileListHWM(folder=folder, value=1)

    with pytest.raises(ValueError):
        FileListHWM(folder=folder, value=valid_value, process=1)

    with pytest.raises(ValueError):
        FileListHWM(folder=folder, value=invalid_value, process=process)

    if invalid_file != "":
        with pytest.raises(ValueError):
            FileListHWM(folder=folder, value=invalid_file, process=process)


def test_file_list_hwm_with_value():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    value = [file1, file2, file2]
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")

    hwm = FileListHWM(folder=folder)

    hwm1 = hwm.with_value(value)
    assert RelativePath(file1) in hwm1
    assert file2 in hwm1

    hwm2 = hwm.with_value(file1)
    assert file1 in hwm2
    assert file2 not in hwm2

    hwm3 = hwm.with_value(file2)
    assert file1 not in hwm3
    assert file2 in hwm3

    with pytest.raises(ValueError):
        hwm.with_value("/root/path")

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(folder)

    with pytest.raises((TypeError, ValueError)):
        hwm.with_value(hwm1)


def test_file_list_hwm_frozen():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    value = [file1, file2]
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")

    hwm = FileListHWM(folder=folder)

    for attr in ("value", "folder", "process"):
        for item in (1, "abc", None, folder, process, file1, file2, value):

            with pytest.raises(TypeError):
                setattr(hwm, attr, item)


def test_file_list_hwm_compare():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("another.csv")

    value1 = [file1, file2]
    value2 = [file1, file2, file2]
    value3 = [file2, file3]

    folder1 = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")
    folder2 = RemoteFolder(root=AbsolutePath("/home/user/cde"), location="ftp://my.domain:23")

    hwm = FileListHWM(folder=folder1, value=value1)
    hwm_with_doubles = FileListHWM(folder=folder1, value=value2)

    hwm1 = FileListHWM(folder=folder1, value=value1)
    hwm2 = FileListHWM(folder=folder2, value=value1)
    hwm3 = FileListHWM(folder=folder1, value=value3)
    hwm4 = FileListHWM(folder=folder2, value=value3)

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

    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")

    hwm1 = FileListHWM(folder=folder, value=value1)
    hwm2 = FileListHWM(folder=folder, value=value2)

    assert hwm1 + file3 == hwm2
    assert hwm1 + [file3] == hwm2
    assert hwm1 + {file3} == hwm2

    with pytest.raises(TypeError):
        _ = hwm1 + hwm2


def test_file_list_hwm_sub():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("some.orc")

    value1 = [file1, file2]
    value2 = [file1, file2, file3]

    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")

    hwm1 = FileListHWM(folder=folder, value=value1)
    hwm2 = FileListHWM(folder=folder, value=value2)

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
    root = PosixPath("/home/user/abc")
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    file3 = RelativePath("other.py")

    value = [file1, file2]
    folder = RemoteFolder(root=root, location="ftp://my.domain:23")

    hwm = FileListHWM(folder=folder, value=value)

    assert file1 in hwm
    assert RelativePath(file1) in hwm
    assert PosixPath(file1) in hwm
    assert root / file1 in hwm
    assert str(root / file1) in hwm

    assert file3 not in hwm

    with pytest.raises(TypeError):
        assert 1 not in hwm

    with pytest.raises(TypeError):
        assert None not in hwm

    with pytest.raises(TypeError):
        assert folder not in hwm


def test_file_list_hwm_qualified_name():
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")
    process = Process(name="myprocess", host="myhost")

    hwm = FileListHWM(
        folder=folder,
        process=process,
    )
    assert hwm.qualified_name == "downloaded_files#/home/user/abc@ftp://my.domain:23#myprocess@myhost"


def test_file_list_hwm_serialize():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")

    value = [file1, file2, file2]
    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")

    hwm1 = FileListHWM(folder=folder, value=value)
    assert hwm1.serialize() == f"{file2}\n{file1}"  # result is sorted

    hwm2 = FileListHWM(folder=folder)
    assert hwm2.serialize() == ""


def test_file_list_hwm_deserialize():
    file1 = "some/path/file.py"
    file2 = RelativePath("another.csv")
    serialized = "another.csv\nsome/path/file.py\nanother.csv"

    folder = RemoteFolder(root="/home/user/abc", location="ftp://my.domain:23")

    value = FileListHWM.deserialize(serialized)
    assert RelativePath(file1) in value
    assert file2 in value

    hwm = FileListHWM(folder=folder, value=serialized)
    assert file1 in hwm
    assert file2 in hwm

    assert not FileListHWM.deserialize("")

    for wrong_value in [FileListHWM, None]:  # noqa: WPS335
        with pytest.raises((TypeError, ValueError)):
            FileListHWM(folder=folder, value=wrong_value)

    for wrong_value in [FileListHWM, None, []]:  # noqa: WPS335
        with pytest.raises((TypeError, ValueError)):
            FileListHWM.deserialize(wrong_value)
