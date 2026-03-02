.. title

ETL Entities
============

|Repo Status| |PyPI Latest Release| |PyPI License| |PyPI Python Version| |PyPI Downloads|
|Documentation| |CI Status| |Test Coverage| |pre-commit.ci Status|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :alt: Repo status - Active
    :target: https://github.com/MTSWebServices/etl-entities
.. |PyPI Latest Release| image:: https://img.shields.io/pypi/v/etl-entities
    :alt: PyPI - Latest Release
    :target: https://pypi.org/project/etl-entities/
.. |PyPI License| image:: https://img.shields.io/pypi/l/etl-entities.svg
    :alt: PyPI - License
    :target: https://github.com/MTSWebServices/etl-entities/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/etl-entities.svg
    :alt: PyPI - Python Version
    :target: https://pypi.org/project/etl-entities/
.. |PyPI Downloads| image:: https://img.shields.io/pypi/dm/etl-entities
    :alt: PyPI - Downloads
    :target: https://pypi.org/project/etl-entities/
.. |Documentation| image:: https://readthedocs.org/projects/etl-entities/badge/?version=stable
    :alt: Documentation - ReadTheDocs
    :target: https://etl-entities.readthedocs.io/
.. |CI Status| image:: https://github.com/MTSWebServices/etl-entities/workflows/Tests/badge.svg
    :alt: Github Actions - latest CI build status
    :target: https://github.com/MTSWebServices/etl-entities/actions
.. |Test Coverage| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/
    MTSOnGithub/03e73a82ecc4709934540ce8201cc3b4/raw/etl-entities_badge.json
    :target: https://github.com/MTSWebServices/etl-entities/actions
.. |pre-commit.ci Status| image:: https://results.pre-commit.ci/badge/github/MTSWebServices/etl-entities/develop.svg
    :alt: pre-commit.ci - status
    :target: https://results.pre-commit.ci/latest/github/MTSWebServices/etl-entities/develop

What is ETL Entities?
-----------------------

Collection of classes & decorators used for handling High Water Mark (HWM).

Currently implemented:

* HWM classes:
    * ``ColumnIntHWM``
    * ``ColumnDateHWM``
    * ``ColumnDateTimeHWM``
    * ``FileListHWM``
    * ``FileModifiedTimeHWM``
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
