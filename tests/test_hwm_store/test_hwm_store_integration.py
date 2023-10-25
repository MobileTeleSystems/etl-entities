import secrets
from datetime import date, datetime, timedelta
from unittest.mock import Mock

import pytest

from etl_entities.hwm import ColumnDateHWM, ColumnDateTimeHWM, ColumnIntHWM, FileListHWM
from etl_entities.hwm_store import MemoryHWMStore


@pytest.fixture(
    params=[
        (
            ColumnIntHWM(
                name=secrets.token_hex(5),
                column=secrets.token_hex(5),
                value=10,
            ),
            5,
        ),
        (
            ColumnDateHWM(
                name=secrets.token_hex(5),
                column=secrets.token_hex(5),
                value=date(year=2023, month=8, day=15),
            ),
            timedelta(days=31),
        ),
        (
            ColumnDateTimeHWM(
                name=secrets.token_hex(5),
                column=secrets.token_hex(5),
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


@pytest.fixture
def mock_external_process():
    process = Mock()
    process.run = Mock()
    process.update_hwm = Mock(side_effect=lambda hwm, increment: hwm + increment)
    return process


def test_hwm_store_get_save(hwm_delta):
    hwm_store = MemoryHWMStore()
    hwm, delta = hwm_delta
    assert hwm_store.get_hwm(hwm.name) is None

    hwm_store.set_hwm(hwm)
    assert hwm_store.get_hwm(hwm.name) == hwm

    hwm2 = hwm + delta
    hwm_store.set_hwm(hwm2)
    assert hwm_store.get_hwm(hwm.name) == hwm2


def test_memory_hwm_store_integration(hwm_delta, mock_external_process):
    hwm_store = MemoryHWMStore()
    hwm, delta = hwm_delta

    def simulate_process(hwm_store, hwm, delta):
        current_hwm = hwm_store.get_hwm(hwm.name)
        assert current_hwm is None

        mock_external_process.run()

        new_hwm = mock_external_process.update_hwm(hwm, delta)
        hwm_store.set_hwm(new_hwm)
        assert hwm_store.get_hwm(hwm.name) == new_hwm

        another_hwm_increment = delta * 2
        newer_hwm = mock_external_process.update_hwm(new_hwm, another_hwm_increment)
        hwm_store.set_hwm(newer_hwm)
        assert hwm_store.get_hwm(hwm.name) == newer_hwm

        concurrent_process = Mock()
        concurrent_process.update_hwm = Mock(return_value=newer_hwm + delta)
        concurrent_new_hwm = concurrent_process.update_hwm(newer_hwm, delta)
        hwm_store.set_hwm(concurrent_new_hwm)
        assert hwm_store.get_hwm(hwm.name) == concurrent_new_hwm

        return concurrent_new_hwm

    with hwm_store:
        final_expected_hwm = simulate_process(hwm_store, hwm, delta)

    final_hwm = hwm_store.get_hwm(hwm.name)
    assert final_hwm == final_expected_hwm
