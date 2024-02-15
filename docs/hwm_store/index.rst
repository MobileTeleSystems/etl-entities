.. _hwm-store:

What is HWM Store
=================

HWM objects are stored in HWM stores.

Known implementations:
    * :obj:`MemoryHWMStore <etl_entities.hwm_store.memory_hwm_store.MemoryHWMStore>` (RAM)
    * `YAMLHWMStore <https://onetl.readthedocs.io/en/stable/hwm_store/yaml_hwm_store.html>`_ (local file)
    * `HorizonHWMStore <https://horizon-hwm-store.readthedocs.io/en/latest/horizon-hwm-store.html>`_ (external API)

It is also possible to register your own HWN Store using :ref:`register-hwm-store-class`.

You can select store based on dict config using :ref:`detect-hwm-store`.
