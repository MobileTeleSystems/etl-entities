import pytest

from etl_entities.source import Table


@pytest.mark.parametrize("instance", ["proto://url", "proto://url/path", "cluster-name"])
@pytest.mark.parametrize("name", ["name", "schema.name", "db.schema.name"])
def test_table_valid_input(instance, name):
    table = Table(name=name, instance=instance)
    assert table.name == name
    assert table.instance == instance
    assert table.full_name == name
    assert str(table) == name


@pytest.mark.parametrize("invalid_name", ["wrong@name", "wrong#name", []])
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
def test_table_wrong_input(invalid_name, invalid_instance):
    valid_name = "some"

    with pytest.raises(ValueError):
        Table()

    with pytest.raises(ValueError):
        Table(name=valid_name)

    with pytest.raises(ValueError):
        Table(instance=valid_name)

    with pytest.raises(ValueError):
        Table(name=invalid_name, instance=invalid_instance)


def test_table_frozen():
    name = "schema.name"
    instance = "proto://url"

    table1 = Table(name=name, instance=instance)

    for attr in ("name", "instance"):
        for value in (1, "abc", None):
            with pytest.raises(TypeError):
                setattr(table1, attr, value)


def test_table_compare():
    name1 = "db1.name1"
    name2 = "db2.name2"

    instance1 = "proto://url1"
    instance2 = "proto://url2"

    table = Table(name=name1, instance=instance1)

    table1 = Table(name=name1, instance=instance1)
    table2 = Table(name=name2, instance=instance1)
    table3 = Table(name=name1, instance=instance2)
    table4 = Table(name=name2, instance=instance2)

    assert table == table1

    items = (table1, table2, table3, table4)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_table_qualified_name():
    name = "schema.name"
    instance = "http://some.url:234"

    table = Table(
        name=name,
        instance=instance,
    )
    assert table.qualified_name == f"{name}@{instance}"


def test_table_serialization():
    name = "schema.name"
    instance = "proto://url"

    serialized = {"name": name, "instance": instance}
    table = Table(name=name, instance=instance)

    assert table.serialize() == serialized
    assert Table.deserialize(serialized) == table
