import secrets
from datetime import date, datetime

import pytest

from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    HWMTypeRegistry,
)


@pytest.mark.parametrize(
    "hwm_class, hwm_type, value, serialized_value",
    [
        (ColumnDateHWM, "column_date", date(year=2021, month=12, day=1), "2021-12-01"),
        (
            ColumnDateTimeHWM,
            "column_datetime",
            datetime(year=2021, month=12, day=1, hour=4, minute=20, second=33),
            "2021-12-01T04:20:33",
        ),
        (ColumnIntHWM, "column_int", 1, 1),
    ],
)
def test_column_hwm_parse(hwm_class, hwm_type, value, serialized_value):
    name = secrets.token_hex()
    table = "table_name"
    modified_time = datetime.now()

    serialized1 = {
        "value": serialized_value,
        "type": hwm_type,
        "source": table,
        "name": name,
        "modified_time": modified_time.isoformat(),
    }
    hwm1 = hwm_class(name=name, source=table, value=value, modified_time=modified_time)

    assert HWMTypeRegistry.parse(serialized1) == hwm1

    serialized2 = serialized1.copy()
    serialized2["value"] = None
    hwm2 = hwm_class(name=name, source=table, modified_time=modified_time)

    assert HWMTypeRegistry.parse(serialized2) == hwm2

    serialized3 = serialized1.copy()
    serialized3["type"] = "unknown"
    with pytest.raises(KeyError):
        HWMTypeRegistry.parse(serialized3)
