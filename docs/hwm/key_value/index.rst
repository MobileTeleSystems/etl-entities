.. _key_value_hwm_classes:

KeyValue HWM
============

.. toctree::
    :maxdepth: 2
    :caption: HWM classes

    key_value_int_hwm

What is KeyValue HWM?
---------------------

The KeyValue High Water Mark (HWM) is a specialized class designed to manage and track incremental data changes in systems where data is stored or represented as key-value pairs, such as in message queues like Kafka.

Use Case
--------

The ``KeyValueHWM`` class is particularly beneficial in scenarios where there is a need to `incrementally <https://onetl.readthedocs.io/en/stable/strategy/incremental_strategy.html>`_ upload data in an ETL process.

For instance, in typical ETL processes using `Spark with Kafka <https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html>`_, data re-written entirely from all partitions in topics starting from **zero** offset. This approach can be inefficient, time-consuming and create duplicates in target. By leveraging the ``KeyValueIntHWM`` class, it becomes possible to track the last offset of data processed. This enables the ETL process to read data appended to topic since previous run instead of reading the entire topic content each time.

Example Usage with Kafka Messages
---------------------------------

Consider a Kafka topic with several partitions, each having its own offset indicating the latest message.

Initial Kafka Topic State:

.. code:: bash

    Partition 0: Offset 100
    Partition 1: Offset 150
    Partition 2: Offset 200

When a new batch of messages arrives, the offsets in the Kafka partitions are updated:

.. code:: bash

    Partition 0: Offset 110  # 10 new messages
    Partition 1: Offset 155  # 5 new messages
    Partition 2: Offset 200  # No new messages

Using the ``KeyValueIntHWM`` class, we can track these offsets:

.. code:: python

    from etl_entities.hwm import KeyValueIntHWM

    initial_offsets = {
        0: 100,  # Partition 0 offset 100
        1: 150,  # Partition 1 offset 150
        2: 200,  # Partition 2 offset 200
    }

    # Creating an instance of KeyValueIntHWM with initial offsets
    hwm = KeyValueIntHWM(value=initial_offsets, ...)

    # Running some ETL process, which updates the HWM value after finish
    run_etl_process(hwm, new_batch_data)

    # HWM values after running the ETL process
    assert hwm.value == {0: 110, 1: 155, 2: 200}


This approach ensures that only new messages (i.e., those after the last recorded offset in each partition) are considered in the next ETL process. For Partition 0 and Partition 1, the new offsets (110 and 155, respectively) are stored in the HWM, while Partition 2 remains unchanged as there were no new messages.


Restrictions
------------

- **Non-Decreasing Values**: The ``KeyValueHWM`` class is designed to handle only non-decreasing values. During the update process, if the new offset provided for a given partition is less than the current offset, the value will not be updated.

- **Incomplete Key Updates**: If a key is not included in new hwm value, its value remains unchanged. This is essential because keys in systems like Kafka (partitions) cannot be deleted, and their last known position is left intact.
