import pytest

from etl_entities.hwm_store import HWMStoreClassRegistry, MemoryHWMStore


def test_hwm_store_registry_add_and_get():
    class DummyStore(MemoryHWMStore):
        pass  # noqa: WPS604

    HWMStoreClassRegistry.add("dummy_store", DummyStore)
    assert HWMStoreClassRegistry.get("dummy_store") == DummyStore

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
