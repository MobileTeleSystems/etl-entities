import pytest

from hwmlib.source import Column


def test_column_valid_input():
    name = "some"
    partition_name = "abc"
    partition_value = "cde"

    column1 = Column(name=name, partition={partition_name: partition_value})
    assert column1.name == name
    assert column1.partition
    assert column1.partition[partition_name] == partition_value

    column1 = Column(name=name, partition=[(partition_name, partition_value)])
    assert column1.name == name
    assert column1.partition
    assert column1.partition[partition_name] == partition_value

    column2 = Column(name=name)
    assert column2.name == name
    assert not column2.partition


@pytest.mark.parametrize("invalid_name", ["wrong/name", "wrong@name", "wrong=name", "wrong#name", None, frozenset()])
def test_column_wrong_input(invalid_name):
    valid_name = "some"

    with pytest.raises(ValueError):
        Column()

    with pytest.raises(ValueError):
        Column(name=invalid_name)

    with pytest.raises(ValueError):
        Column(partition={valid_name: valid_name})

    with pytest.raises(ValueError):
        Column(name=valid_name, partition={invalid_name: valid_name})

    with pytest.raises(ValueError):
        Column(name=valid_name, partition={valid_name: invalid_name})

    with pytest.raises(ValueError):
        Column(name=invalid_name, partition={valid_name: valid_name})


def test_column_frozen():
    name = "some"
    partition = {"some": "abc", "another": "cde"}

    column1 = Column(name=name, partition=partition)

    for attr in ("name", "partition"):
        for value in (1, "abc", None):

            with pytest.raises(TypeError):
                setattr(column1, attr, value)


def test_column_compare():  # noqa: WPS210
    name1 = "some1"
    name2 = "some2"

    partition1 = {}
    partition2 = {"some1": "value1"}
    partition3 = {"some1": "value2"}
    partition4 = {"some2": "value1"}
    partition5 = {"some2": "value2"}

    column = Column(name=name1, partition=partition1)
    column_partitioned = Column(name=name1, partition=partition2)

    column1 = Column(name=name1, partition=partition1)
    column2 = Column(name=name1, partition=partition2)
    column3 = Column(name=name1, partition=partition3)
    column4 = Column(name=name1, partition=partition4)
    column5 = Column(name=name1, partition=partition5)

    column6 = Column(name=name2, partition=partition1)
    column7 = Column(name=name2, partition=partition2)
    column8 = Column(name=name2, partition=partition3)
    column9 = Column(name=name2, partition=partition4)
    column10 = Column(name=name2, partition=partition5)

    assert column == column1
    assert column_partitioned == column2

    items = (column1, column2, column3, column4, column5, column6, column7, column8, column9, column10)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


@pytest.mark.parametrize(
    "partition, partition_qualified_name",
    [({"some1": "value1", "some2": "value2"}, "|some1=value1/some2=value2"), ({}, "")],
)
def test_column_qualified_name(
    partition,
    partition_qualified_name,
):
    name = "some"

    column = Column(
        name=name,
        partition=partition,
    )
    assert column.qualified_name == f"{name}{partition_qualified_name}"
