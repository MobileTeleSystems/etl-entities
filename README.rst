.. title

ETL Entities
============

|Repo Status| |PyPI| |PyPI License| |PyPI Python Version|
|Documentation| |Build Status| |Coverage| |pre-commit.ci|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://github.com/MobileTeleSystems/etl-entities
.. |PyPI| image:: https://img.shields.io/pypi/v/etl-entities
    :target: https://pypi.org/project/etl-entities/
.. |PyPI License| image:: https://img.shields.io/pypi/l/etl-entities.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/etl-entities.svg
    :target: https://badge.fury.io/py/etl-entities
.. |Documentation| image:: https://readthedocs.org/projects/etl-entities/badge/?version=stable
    :target: https://etl-entities.readthedocs.io/
.. |Build Status| image:: https://github.com/MobileTeleSystems/etl-entities/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/actions
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/etl-entities/branch/develop/graph/badge.svg?token=RIO8URKNZJ
    :target: https://codecov.io/gh/MobileTeleSystems/etl-entities
.. |pre-commit.ci| image:: https://results.pre-commit.ci/badge/github/MobileTeleSystems/etl-entities/develop.svg
    :target: https://results.pre-commit.ci/latest/github/MobileTeleSystems/etl-entities/develop

What is ETL Entities?
-----------------------

Collection of classes & decorators used for handling High Water Mark (HWM).

Currently implemented:

* HWM classes:
    * ``ColumnIntHWM``
    * ``ColumnDateHWM``
    * ``ColumnDateTimeHWM``
    * ``FileListHWM``
    * ``KeyValueIntHWM``

* HWM Store classes:
    * ``BaseHWMStore`` (base interface)
    * ``MemoryHWMStore``

.. installation

How to install
---------------

.. code:: bash

    pip install etl-entities

.. documentation

Documentation
-------------

See https://etl-entities.readthedocs.io/
