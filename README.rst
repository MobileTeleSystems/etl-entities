.. title

ETL Entities
============

|Repo Status| |PyPI| |PyPI License| |PyPI Python Version|
|Documentation| |Build Status| |Coverage|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://github.com/MobileTeleSystems/etl-entities
.. |PyPI| image:: https://img.shields.io/pypi/v/etl-entities
    :target: https://pypi.org/project/etl-entities/
.. |PyPI License| image:: https://img.shields.io/pypi/l/etl-entities.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/etl-entities.svg
    :target: https://badge.fury.io/py/etl-entities
.. |Build Status| image:: https://github.com/MobileTeleSystems/etl-entities/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/actions
.. |Documentation| image:: https://readthedocs.org/projects/etl-entities/badge/?version=stable
    :target: https://etl-entities.readthedocs.io/
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/etl-entities/branch/develop/graph/badge.svg?token=RIO8URKNZJ
    :target: https://codecov.io/gh/MobileTeleSystems/etl-entities

What is ETL Entities?
-----------------------

Collection of classes & decorators used for handling High Water Mark (HWM).

Currently implemented:
    * ``ColumnIntHWM``
    * ``ColumnDateHWM``
    * ``ColumnDateTimeHWM``
    * ``FileListHWM``
    * ``KeyValueIntHWM``
    * ``MemoryHWMStore``
    * ``BaseHWMStore`` (interface for third-party HWM store implementations)

.. installation

How to install
---------------

.. code:: bash

    pip install etl-entities

.. documentation

Documentation
-------------

See https://etl-entities.readthedocs.io/

.. contribution

Contribution guide
-------------------

See `<CONTRIBUTING.rst>`__

.. security

Security
-------------------

See `<SECURITY.rst>`__
