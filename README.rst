.. title

HWM lib
==============================
|Build Status| |Documentation| |PyPI|

.. |Build Status| image:: https://gitlab.services.mts.ru/bigdata/platform/onetools/etl-entities/badges/develop/pipeline.svg
    :target: https://gitlab.services.mts.ru/bigdata/platform/onetools/etl-entities/-/pipelines
.. |Documentation| image:: https://img.shields.io/badge/docs-latest-success
    :target: https://bigdata.pages.mts.ru/platform/onetools/etl-entities/
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

See https://bigdata.pages.mts.ru/platform/onetools/etl-entities/

.. contribution

Contribution guide
-------------------

See `<CONTRIBUTING.rst>`__


.. contribution

Contribution guide
-------------------

See https://wiki.bd.msk.mts.ru/display/DAT/Contribution+guide

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

.. develops

Development
---------------

Testing
~~~~~~~~

Running tests is as simple as:

.. code-block:: bash

    pytest
