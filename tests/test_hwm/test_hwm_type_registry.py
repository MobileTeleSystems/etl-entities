from datetime import date, datetime

import pytest

from etl_entities.hwm import DateHWM, DateTimeHWM, HWMTypeRegistry, IntHWM
from etl_entities.process import Process
from etl_entities.source import Column, Table


@pytest.mark.parametrize(
    "hwm_class, hwm_type, value, serialized_value",
    [
        (DateHWM, "date", date(year=2021, month=12, day=1), "2021-12-01"),
        (
            DateTimeHWM,
            "datetime",
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
        ),
        (IntHWM, "int", 1, "1"),
    ],
)
def test_column_hwm_parse(hwm_class, hwm_type, value, serialized_value):
    column = Column(name="some")
    table = Table(name="abc.another", instance="proto://url")
    process = Process(name="abc", host="somehost", task="sometask", dag="somedag")
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value,
        "type": hwm_type,
        "column": column.serialize(),
        "source": table.serialize(),
        "process": process.serialize(),
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = hwm_class(column=column, source=table, value=value, process=process, modified_time=modified_time)

    assert HWMTypeRegistry.parse(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = None
    hwm2 = hwm_class(column=column, source=table, process=process, modified_time=modified_time)

    assert HWMTypeRegistry.parse(serialized2) == hwm2

    serialized3 = serialized1.copy()
    serialized3["type"] = "unknown"
    with pytest.raises(KeyError):
        HWMTypeRegistry.parse(serialized3)
