from pathlib import PosixPath

import pytest

from etl_entities.source import RemoteFolder


@pytest.mark.parametrize(
    "valid_name",
    [
        "/some",
        "/some.file",
        "/some/path",
        "/some/folder/file.name",
    ],
)
@pytest.mark.parametrize(
    "valid_instance",
    ["rnd-dwh", "ftp://some:1234", "cde://192.168.1.1"],
)
def test_remote_folder_valid_input(valid_name, valid_instance):
    remote_folder1 = RemoteFolder(name=valid_name, instance=valid_instance)
    assert str(remote_folder1.name) == valid_name
    assert remote_folder1.instance == valid_instance

    assert remote_folder1.full_name == valid_name
    assert str(remote_folder1) == valid_name


@pytest.mark.parametrize(
    "invalid_name",
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
    "invalid_instance",
    [
        1,
        None,
        [],
        "",
        "001",
        "*",
        "some*",
        "some-",
        "some_",
        "*some",
        "-some",
        "_some",
        "001some",
        "001-some",
        "001_some",
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
    ],
)
def test_remote_folder_wrong_input(invalid_name, invalid_instance):
    valid_name = "/some/path"
    valid_instance = "proto://url"

    with pytest.raises(ValueError):
        RemoteFolder()

    with pytest.raises(ValueError):
        RemoteFolder(name=valid_name)

    with pytest.raises(ValueError):
        RemoteFolder(instance=valid_instance)

    with pytest.raises(ValueError):
        RemoteFolder(name=invalid_name, instance=valid_instance)

    with pytest.raises(ValueError):
        RemoteFolder(name=valid_name, instance=invalid_instance)


def test_remote_folder_frozen():
    name = "/some/path"
    instance = "proto://url"

    remote_folder = RemoteFolder(name=name, instance=instance)

    for attr in ("name", "instance"):
        for value in (1, ".", "/abc", None, PosixPath()):

            with pytest.raises(TypeError):
                setattr(remote_folder, attr, value)


def test_remote_folder_compare():
    name1 = "/some/path1"
    name2 = "/some/path2"

    instance1 = "proto://url1"
    instance2 = "proto://url2"

    remote_folder = RemoteFolder(name=name1, instance=instance1)

    remote_folder1 = RemoteFolder(name=name1, instance=instance1)
    remote_folder2 = RemoteFolder(name=name2, instance=instance1)
    remote_folder3 = RemoteFolder(name=name1, instance=instance2)
    remote_folder4 = RemoteFolder(name=name2, instance=instance2)

    assert remote_folder == remote_folder1

    items = (remote_folder1, remote_folder2, remote_folder3, remote_folder4)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_remote_folder_qualified_name():
    name = "/some/path"
    instance = "http://some.url:234"

    remote_folder = RemoteFolder(
        name=name,
        instance=instance,
    )
    assert remote_folder.qualified_name == f"{name}@{instance}"


def test_remote_folder_serialization():
    name = "/some/path"
    instance = "http://some.url:234"

    serialized = {"name": name, "instance": instance}
    remote_folder = RemoteFolder(
        name=name,
        instance=instance,
    )

    assert remote_folder.serialize() == serialized
    assert RemoteFolder.deserialize(serialized) == remote_folder
