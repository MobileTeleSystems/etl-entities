import pytest

from etl_entities.source import Table


@pytest.mark.parametrize("instance", ["proto://url", "proto://url/path", "cluster-name"])
def test_table_valid_input(instance):
    name = "some"
    db = "another"

    table1 = Table(name=name, db=db, instance=instance)
    assert table1.name == name
    assert table1.db == db
    assert table1.instance == instance


@pytest.mark.parametrize("invalid_name", ["wrong.name", "wrong@name", "wrong#name", []])
@pytest.mark.parametrize("invalid_db", ["wrong.name", "wrong@name", "wrong#name", []])
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
def test_table_wrong_input(invalid_name, invalid_db, invalid_instance):
    valid_name = "some"
    valid_db = "another"
    valid_instance = "proto://url"

    with pytest.raises(ValueError):
        Table()

    with pytest.raises(ValueError):
        Table(name=valid_name)

    with pytest.raises(ValueError):
        Table(db=valid_name)

    with pytest.raises(ValueError):
        Table(instance=valid_name)

    with pytest.raises(ValueError):
        Table(name=valid_name, db=valid_db)

    with pytest.raises(ValueError):
        Table(name=valid_name, instance=valid_instance)

    with pytest.raises(ValueError):
        Table(db=valid_db, instance=valid_instance)

    with pytest.raises(ValueError):
        Table(name=invalid_name, db=valid_db, instance=valid_instance)

    with pytest.raises(ValueError):
        Table(name=valid_name, db=invalid_db, instance=valid_instance)

    with pytest.raises(ValueError):
        Table(name=valid_name, db=valid_db, instance=invalid_instance)


def test_table_frozen():
    name = "some"
    db = "another"
    instance = "proto://url"

    table1 = Table(name=name, db=db, instance=instance)

    for attr in ("name", "db", "instance"):
        for value in (1, "abc", None):

            with pytest.raises(TypeError):
                setattr(table1, attr, value)


def test_table_compare():
    name1 = "some1"
    name2 = "some2"

    db1 = "db1"
    db2 = "db2"

    instance1 = "proto://url1"
    instance2 = "proto://url2"

    table = Table(name=name1, db=db1, instance=instance1)

    table1 = Table(name=name1, db=db1, instance=instance1)
    table2 = Table(name=name2, db=db1, instance=instance1)
    table3 = Table(name=name1, db=db2, instance=instance1)
    table4 = Table(name=name2, db=db2, instance=instance1)
    table5 = Table(name=name1, db=db1, instance=instance2)
    table6 = Table(name=name2, db=db1, instance=instance2)
    table7 = Table(name=name1, db=db2, instance=instance2)
    table8 = Table(name=name2, db=db2, instance=instance2)

    assert table == table1

    items = (table1, table2, table3, table4, table5, table6, table7, table8)

    for item1 in items:
        for item2 in items:
            if item1 is not item2:
                assert item1 != item2


def test_table_qualified_name():
    name = "some"
    db = "another"
    instance = "http://some.url:234"

    table = Table(
        name=name,
        db=db,
        instance=instance,
    )
    assert table.qualified_name == f"{db}.{name}@{instance}"
