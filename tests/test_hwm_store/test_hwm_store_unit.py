import pytest

from etl_entities.hwm_store import (
    HWMStoreClassRegistry,
    HWMStoreManager,
    MemoryHWMStore,
)


def test_hwm_store_manager_push_and_pop():
    store1 = MemoryHWMStore()
    store2 = MemoryHWMStore()

    assert HWMStoreManager.get_current_level() == 0

    HWMStoreManager.push(store1)
    assert HWMStoreManager.get_current_level() == 1
    assert HWMStoreManager.get_current() is store1

    HWMStoreManager.push(store2)
    assert HWMStoreManager.get_current_level() == 2
    assert HWMStoreManager.get_current() is store2

    assert HWMStoreManager.pop() is store2
    assert HWMStoreManager.get_current_level() == 1
    assert HWMStoreManager.get_current() is store1

    assert HWMStoreManager.pop() is store1
    assert HWMStoreManager.get_current_level() == 0


def test_hwm_store_manager_empty_pop():
    with pytest.raises(IndexError):
        HWMStoreManager.pop()


def test_hwm_store_registry_add_and_get():
    class DummyStore(MemoryHWMStore):
        pass  # noqa: WPS604

    HWMStoreClassRegistry.add("dummy", DummyStore)
    assert HWMStoreClassRegistry.get("dummy") == DummyStore

    with pytest.raises(KeyError):
        HWMStoreClassRegistry.get("nonexistent")


def test_hwm_store_registry_set_default():
    class DefaultStore(MemoryHWMStore):
        pass  # noqa: WPS604

    HWMStoreClassRegistry.set_default(DefaultStore)
    assert HWMStoreClassRegistry.get() == DefaultStore


def test_hwm_store_registry_known_types():
    class KnownTypeStore(MemoryHWMStore):
        pass  # noqa: WPS604

    HWMStoreClassRegistry.add("known", KnownTypeStore)
    known_types = HWMStoreClassRegistry.known_types()
    assert "known" in known_types
