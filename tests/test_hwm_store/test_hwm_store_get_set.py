import os
import secrets
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

from etl_entities.hwm import (
    ColumnDateHWM,
    ColumnDateTimeHWM,
    ColumnIntHWM,
    FileListHWM,
    FileModifiedTimeHWM,
    KeyValueIntHWM,
)
from etl_entities.hwm_store import MemoryHWMStore


def file_with_mtime(mtime: datetime) -> Path:
    result = Mock(spec=Path)
    result.exists.return_value = True
    result.is_file.return_value = True
    result_stat = Mock(spec=os.stat_result)
    result_stat.st_mtime = mtime.timestamp()
    result.stat.return_value = result_stat
    return result


@pytest.fixture(
    params=[
        (
            ColumnIntHWM(
                name=secrets.token_hex(5),
                # no source
                value=10,
            ),
            5,
        ),
        (
            ColumnIntHWM(
                name=secrets.token_hex(5),
                source=secrets.token_hex(5),
                value=10,
            ),
            5,
        ),
        (
            ColumnDateHWM(
                name=secrets.token_hex(5),
                source=secrets.token_hex(5),
                value=date(2025, 1, 1),
            ),
            date(2025, 1, 2),
        ),
        (
            ColumnDateTimeHWM(
                name=secrets.token_hex(5),
                source=secrets.token_hex(5),
                value=datetime(2025, 1, 1, 11, 22, 33, 456789),
            ),
            datetime(2025, 1, 1, 22, 33, 44, 567890),
        ),
        (
            KeyValueIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                # no topic
                expression="offset",
                value={
                    0: 100,
                    1: 123,
                },
            ),
            {
                0: 110,
                1: 150,
            },
        ),
        (
            KeyValueIntHWM(
                name=f"{secrets.token_hex(5)}.{secrets.token_hex(5)}",
                topic="topic_name",
                expression="offset",
                value={
                    0: 100,
                    1: 123,
                },
            ),
            {
                0: 110,
                1: 150,
            },
        ),
        (
            FileListHWM(
                name=secrets.token_hex(5),
                # no directory
                value=["/some/path", "/another.file"],
            ),
            "/third.file",
        ),
        (
            FileListHWM(
                name=secrets.token_hex(5),
                directory="/absolute/path",
                value=["/absolute/path/file1", "/absolute/path/file2"],
            ),
            "/absolute/path/file3",
        ),
        (
            FileModifiedTimeHWM(
                name=secrets.token_hex(5),
                # no directory
                value=datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc),
            ),
            file_with_mtime(datetime(2025, 1, 1, 22, 33, 44, 567890, tzinfo=timezone.utc)),
        ),
        (
            FileModifiedTimeHWM(
                name=secrets.token_hex(5),
                directory="/absolute/path",
                value=datetime(2025, 1, 1, 11, 22, 33, 456789, tzinfo=timezone.utc),
            ),
            file_with_mtime(datetime(2025, 1, 1, 22, 33, 44, 567890, tzinfo=timezone.utc)),
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
    hwm1 = hwm.copy().update(delta)
    assert hwm_store.get_hwm(hwm.name) == hwm

    # it is changed only after explicit call of .set_hwm()
    hwm_store.set_hwm(hwm1)
    assert hwm_store.get_hwm(hwm.name) == hwm1
