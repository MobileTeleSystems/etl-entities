import secrets
from datetime import date, datetime, timedelta

import pytest

from etl_entities.hwm import ColumnDateHWM, ColumnDateTimeHWM, ColumnIntHWM, FileListHWM
from etl_entities.hwm_store import MemoryHWMStore


@pytest.fixture(
    params=[
        (
            ColumnIntHWM(
                name=secrets.token_hex(5),
                value=10,
            ),
            5,
        ),
        (
            ColumnDateHWM(
                name=secrets.token_hex(5),
                value=date(year=2023, month=8, day=15),
            ),
            timedelta(days=31),
        ),
        (
            ColumnDateTimeHWM(
                name=secrets.token_hex(5),
                value=datetime(year=2023, month=8, day=15, hour=11, minute=22, second=33),
            ),
            timedelta(seconds=50),
        ),
        (
            FileListHWM(
                name=secrets.token_hex(5),
                directory=f"/absolute/{secrets.token_hex(5)}",
                value=["some/path", "another.file"],
            ),
            "third.file",
        ),
    ],
)
def hwm_delta(request):
    return request.param


def test_hwm_store_get_save(hwm_delta):
    hwm_store = MemoryHWMStore()
    hwm, delta = hwm_delta
    assert hwm_store.get_hwm(hwm.name) is None

    hwm_store.set_hwm(hwm)
    assert hwm_store.get_hwm(hwm.name) == hwm

    # changing HWM object does not change MemoryHWMStore data
    hwm1 = hwm.copy() + delta
    assert hwm_store.get_hwm(hwm.name) == hwm

    # it is changed only after explicit call of .set_hwm()
    hwm_store.set_hwm(hwm1)
    assert hwm_store.get_hwm(hwm.name) == hwm1
