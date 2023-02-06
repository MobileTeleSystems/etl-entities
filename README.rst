.. title

HWM lib
==============================
|Build Status| |Documentation| |PyPI|

.. |Build Status| image:: https://github.com/MobileTeleSystems/etl-entities/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/actions
.. |ReadTheDocs| image:: https://img.shields.io/readthedocs/etl-entities.svg
    :target: https://etl-entities.readthedocs.io
.. |PyPI| image:: https://img.shields.io/badge/pypi-download-orange
    :target: http://rep.msk.mts.ru/ui/packages/pypi:%2F%2Fetl-entities?name=etl-entities&type=packages

What is ETL Entities?
-----------------------

Collection of classes used for handling High Water Mark (HWM) and gathering Lineage graph.

Currently implemented:
    * ``IntHWM``
    * ``DateHWM``
    * ``DateTimeHWM``
    * ``FileListHWM``
    * ``Column``
    * ``Table``
    * ``RemoteFolder``
    * ``Process``

**Supports only Python == 3.7**

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

.. install

Installation
---------------

Stable release
~~~~~~~~~~~~~~~

Stable version is released on every tag to ``master`` branch. Please use stable releases on production environment.
Version example: ``1.1.2``

.. code:: bash

    pip install etl-entities==1.1.2 # exact version

    pip install etl-entities # latest release

Development release
~~~~~~~~~~~~~~~~~~~~

Development version is released on every tag to ``develop`` branch. Please use development releases **only** for testing purposes.
Version example: ``1.1.2.dev345``

.. code:: bash

    pip install etl-entities==1.1.2dev345 # exact version

    pip install -e etl-entities # latest pre-release

.. tests

Tests
-------

Running tests is as simple as:

.. code-block:: bash

    pytest
