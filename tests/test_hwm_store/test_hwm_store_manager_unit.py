import pytest

from etl_entities.hwm_store import HWMStoreStackManager, MemoryHWMStore


def test_hwm_store_manager_push_and_pop():
    store1 = MemoryHWMStore()
    store2 = MemoryHWMStore()

    assert HWMStoreStackManager.get_current_level() == 0

    HWMStoreStackManager.push(store1)
    assert HWMStoreStackManager.get_current_level() == 1
    assert HWMStoreStackManager.get_current() is store1

    HWMStoreStackManager.push(store2)
    assert HWMStoreStackManager.get_current_level() == 2
    assert HWMStoreStackManager.get_current() is store2

    assert HWMStoreStackManager.pop() is store2
    assert HWMStoreStackManager.get_current_level() == 1
    assert HWMStoreStackManager.get_current() is store1

    assert HWMStoreStackManager.pop() is store1
    assert HWMStoreStackManager.get_current_level() == 0


def test_hwm_store_manager_empty_pop_error():
    with pytest.raises(IndexError):
        HWMStoreStackManager.pop()


def test_hwm_store_context_behavior():
    store_outside = MemoryHWMStore()
    store_with_context = MemoryHWMStore()

    HWMStoreStackManager.push(store_outside)
    assert HWMStoreStackManager.get_current() is store_outside

    with store_with_context:
        assert HWMStoreStackManager.get_current() is store_with_context

    assert HWMStoreStackManager.get_current() is store_outside
