from pathlib import PosixPath

import pytest

from hwmlib.process import Process


@pytest.mark.parametrize("valid_name", ["some", "some process name"])
@pytest.mark.parametrize(
    "valid_host",
    [
        "some",
        "some.domain",
        "some.domain.com",
        "1.2.3.4",
    ],
)
def test_process_valid_input(valid_name, valid_host):
    process1 = Process(name=valid_name, host=valid_host)
    assert process1.name == valid_name
    assert process1.host == valid_host

    process2 = Process(name=valid_name)
    assert process2.name == valid_name
    assert process2.host

    process2 = Process(host=valid_host)
    assert process2.name
    assert process2.host == valid_host


@pytest.mark.parametrize(
    "invalid_host",
    [None, "", "some.*", "localhost", "127.0.0.1", "127.1.1.1", "::1", "0:0:0:0:0:0:0:1", []],
)
def test_process_wrong_input(invalid_host):
    name = "some"

    with pytest.raises(ValueError):
        Process(host=invalid_host)

    with pytest.raises(ValueError):
        Process(name=name, host=invalid_host)


def test_process_frozen():
    name = "some"
    host = "domain"

    process = Process(name=name, host=host)

    for attr in ("name", "host"):
        for value in (1, ".", "/abc", None, PosixPath()):

            with pytest.raises(TypeError):
                setattr(process, attr, value)


def test_process_compare():
    name1 = "some1"
    name2 = "some 2"

    host1 = "domain1"
    host2 = "domain2"

    process = Process(name=name1, host=host1)

    process1 = Process(name=name1, host=host1)
    process2 = Process(name=name2, host=host1)
    process3 = Process(name=name1, host=host2)
    process4 = Process(name=name2, host=host2)

    assert process == process1

    items = (process1, process2, process3, process4)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_process_qualified_name():
    name = "some process name"
    host = "some.domain"

    process = Process(
        name=name,
        host=host,
    )
    assert process.qualified_name == f"{name}@{host}"
