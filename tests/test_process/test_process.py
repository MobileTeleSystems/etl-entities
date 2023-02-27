from pathlib import PosixPath

import pytest

from etl_entities.process import Process


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
@pytest.mark.parametrize(
    "valid_task",
    [
        "abc",
        "a_b_c",
        "some123",
        "some_123",
    ],
)
@pytest.mark.parametrize(
    "valid_dag",
    [
        "abc",
        "a_b_c",
        "some123",
        "some_123",
    ],
)
def test_process_valid_input(valid_name, valid_host, valid_task, valid_dag):
    process1 = Process(name=valid_name, host=valid_host, task=valid_task, dag=valid_dag)
    assert process1.name == valid_name
    assert process1.host == valid_host
    assert process1.task == valid_task
    assert process1.dag == valid_dag

    assert process1.full_name == f"{valid_dag}.{valid_task}.{valid_name}"
    assert str(process1) == f"{valid_dag}.{valid_task}.{valid_name}"

    process2 = Process(name=valid_name, host=valid_host)
    assert process2.name == valid_name
    assert process2.host == valid_host
    assert not process2.task
    assert not process2.dag

    assert process2.full_name == valid_name
    assert str(process2) == valid_name

    process3 = Process(name=valid_name)
    assert process3.name == valid_name
    assert process3.host
    assert not process3.task
    assert not process3.dag

    assert process3.full_name == valid_name
    assert str(process3) == valid_name

    process4 = Process(host=valid_host)
    assert process4.name
    assert process4.host == valid_host
    assert not process3.task
    assert not process3.dag

    assert process4.full_name == process4.name
    assert str(process4) == process4.name

    process5 = Process()
    assert process5.name
    assert process5.host
    assert not process5.task
    assert not process5.dag

    assert process5.full_name == process5.name
    assert str(process5) == process5.name


@pytest.mark.parametrize(
    "invalid_host",
    [None, "", "abc.*", "@abc", "/abc", ":abc", []],
)
@pytest.mark.parametrize(
    "invalid_task",
    [
        "ab.c",
        "a_b.c",
        "some.123",
    ],
)
@pytest.mark.parametrize(
    "invalid_dag",
    [
        "ab.c",
        "a_b.c",
        "some.123",
    ],
)
def test_process_wrong_input(invalid_host, invalid_task, invalid_dag):
    name = "some"
    host = "current"
    task = "abc"
    dag = "cde"

    with pytest.raises(ValueError):
        Process(host=invalid_host)

    with pytest.raises(ValueError):
        Process(task=task)

    with pytest.raises(ValueError):
        Process(dag=dag)

    with pytest.raises(ValueError):
        Process(name=name, host=invalid_host)

    with pytest.raises(ValueError):
        Process(name=name, host=host, task=task)

    with pytest.raises(ValueError):
        Process(name=name, host=host, dag=dag)

    with pytest.raises(ValueError):
        Process(name=name, host=host, task=invalid_task, dag=dag)

    with pytest.raises(ValueError):
        Process(name=name, host=host, task=task, dag=invalid_dag)


def test_process_frozen():
    name = "some"
    host = "domain"
    task = "abc"
    dag = "cde"

    process = Process(name=name, host=host, task=task, dag=dag)

    for attr in ("name", "host", "task", "dag"):
        for value in (1, ".", "/abc", None, PosixPath()):
            with pytest.raises(TypeError):
                setattr(process, attr, value)


def test_process_compare():
    name1 = "some1"
    name2 = "some 2"

    host1 = "domain1"
    host2 = "domain2"

    task1 = "task1"
    task2 = "task2"

    dag1 = "dag1"
    dag2 = "dag2"

    process = Process(name=name1, host=host1)

    process1 = Process(name=name1, host=host1)
    process2 = Process(name=name2, host=host1)
    process3 = Process(name=name1, host=host2)
    process4 = Process(name=name2, host=host2)

    process5 = Process(name=name1, host=host1, task=task1, dag=dag1)
    process6 = Process(name=name2, host=host1, task=task2, dag=dag1)
    process7 = Process(name=name1, host=host2, task=task1, dag=dag2)
    process8 = Process(name=name2, host=host2, task=task2, dag=dag2)

    assert process == process1

    items = (process1, process2, process3, process4, process5, process6, process7, process8)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


@pytest.mark.parametrize(
    "task, dag, prefix",
    [
        ("", "", ""),
        ("abc", "cde", "cde.abc."),
    ],
)
def test_process_qualified_name(task, dag, prefix):
    name = "some process name"
    host = "some.domain"

    process = Process(
        name=name,
        host=host,
        task=task,
        dag=dag,
    )
    assert process.qualified_name == f"{prefix}{name}@{host}"


@pytest.mark.parametrize(
    "task, dag",
    [
        ("", ""),
        ("abc", "cde"),
    ],
)
def test_process_serialization(task, dag):
    name = "some"
    host = "127.0.0.1"

    serialized = {"name": name, "host": host, "task": task, "dag": dag}
    process = Process(name=name, host=host, task=task, dag=dag)

    assert process.serialize() == serialized
    assert Process.deserialize(serialized) == process
