from pathlib import PosixPath

import pytest

from hwmlib.source import RemoteFolder


@pytest.mark.parametrize(
    "valid_root, name",
    [
        ("/some", "some"),
        ("/some.file", "some.file"),
        ("/some/path", "path"),
        ("/some/folder/file.name", "file.name"),
    ],
)
@pytest.mark.parametrize(
    "valid_location",
    ["http://some", "hdfs://some.file", "hive://some/path", "abc://some:1234", "cde://192.168.1.1"],
)
def test_remote_folder_valid_input(valid_root, name, valid_location):
    remote_folder1 = RemoteFolder(root=valid_root, location=valid_location)
    assert str(remote_folder1.root) == valid_root
    assert remote_folder1.location == valid_location
    assert remote_folder1.name == name


@pytest.mark.parametrize(
    "invalid_root",
    [
        1,
        None,
        [],
        ".",
        "..",
        "../another",
        "some.file/../another",
        "some",
        "some.file",
        "some/path",
        "some/folder/file.name",
        "/some/folder@name",
        "/some/folder#name",
    ],
)
@pytest.mark.parametrize(
    "invalid_location",
    [
        1,
        None,
        [],
        "",
        "no_schema",
        "http:/",
        "http://",
        "http:///",
        "123://some",
        "http://some*",
        "http://some:port",
        "http://user@some:1234",
        "http://user:password@some:1234",
        "http://some/path?query",
        "http://some/path#fragment",
        "http://localhost",
        "http://0.0.0.0",
        "http://127.0.0.1",
        "http://127.1.1.1",
        "http://240.0.0.0",
        "http://255.255.255.255",
        "http://::1",
        "http://0:0:0:0:0:0:0:1",
    ],
)
def test_remote_folder_wrong_input(invalid_root, invalid_location):
    valid_root = "/some/path"
    valid_location = "proto://url"

    with pytest.raises(ValueError):
        RemoteFolder()

    with pytest.raises(ValueError):
        RemoteFolder(root=valid_root)

    with pytest.raises(ValueError):
        RemoteFolder(location=valid_location)

    with pytest.raises(ValueError):
        RemoteFolder(root=invalid_root, location=valid_location)

    with pytest.raises(ValueError):
        RemoteFolder(root=valid_root, location=invalid_location)


def test_remote_folder_frozen():
    root = "/some/path"
    location = "proto://url"

    remote_folder = RemoteFolder(root=root, location=location)

    for attr in ("root", "location"):
        for value in (1, ".", "/abc", None, PosixPath()):

            with pytest.raises(TypeError):
                setattr(remote_folder, attr, value)


def test_remote_folder_compare():
    root1 = "/some/path1"
    root2 = "/some/path2"

    location1 = "proto://url1"
    location2 = "proto://url2"

    remote_folder = RemoteFolder(root=root1, location=location1)

    remote_folder1 = RemoteFolder(root=root1, location=location1)
    remote_folder2 = RemoteFolder(root=root2, location=location1)
    remote_folder3 = RemoteFolder(root=root1, location=location2)
    remote_folder4 = RemoteFolder(root=root2, location=location2)

    assert remote_folder == remote_folder1

    items = (remote_folder1, remote_folder2, remote_folder3, remote_folder4)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_remote_folder_qualified_name():
    root = "/some/path"
    location = "http://some.url:234"

    remote_folder = RemoteFolder(
        root=root,
        location=location,
    )
    assert remote_folder.qualified_name == f"{root}@{location}"
