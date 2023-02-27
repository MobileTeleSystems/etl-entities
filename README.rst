.. title

ETL Entities lib
================
|Repo Status| |PyPI| |PyPI License| |PyPI Python Version|
|Documentation| |Build Status| |Coverage|

.. |Repo Status| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://www.repostatus.org/#active
.. |PyPI| image:: https://img.shields.io/pypi/v/etl-entities
    :target: https://pypi.org/project/etl-entities/
.. |PyPI License| image:: https://img.shields.io/pypi/l/etl-entities.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/blob/develop/LICENSE.txt
.. |PyPI Python Version| image:: https://img.shields.io/pypi/pyversions/etl-entities.svg
    :target: https://badge.fury.io/py/etl-entities
.. |ReadTheDocs| image:: https://img.shields.io/readthedocs/etl-entities.svg
    :target: https://etl-entities.readthedocs.io
.. |Build Status| image:: https://github.com/MobileTeleSystems/etl-entities/workflows/Tests/badge.svg
    :target: https://github.com/MobileTeleSystems/etl-entities/actions
.. |Documentation| image:: https://readthedocs.org/projects/etl-entities/badge/?version=stable
    :target: https://etl-entities.readthedocs.io/en/latest/?badge=stable
.. |Coverage| image:: https://codecov.io/gh/MobileTeleSystems/etl-entities/branch/develop/graph/badge.svg?token=RIO8URKNZJ
    :target: https://codecov.io/gh/MobileTeleSystems/etl-entities

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

.. develops

Develop
-------

Clone repo
~~~~~~~~~~

Clone repo:

.. code:: bash

    git clone git@github.com:MobileTeleSystems/etl-entities.git -b develop

    cd etl-entities

Setup environment
~~~~~~~~~~~~~~~~~

Create virtualenv and install dependencies:

.. code:: bash

    # create virtual environment
    python -m venv venv
    source venv/bin/activate
    pip install -U wheel
    pip install -U pip setuptools

    # install requirements
    pip install -U -r requirements.txt

Install dependencies for development:

.. code:: bash

    # install linters, formatters, etc
    pip install -U -r requirements-dev.txt

Enable pre-commit hooks
~~~~~~~~~~~~~~~~~~~~~~~

Install pre-commit hooks:

.. code:: bash

    pre-commit install --install-hooks

Test pre-commit hooks run:

.. code:: bash

    pre-commit run

Run tests
~~~~~~~~~

.. code:: bash

    # install requirements for testing
    pip install -U -r requirements-test.txt

    # run tests
    pytest

Build documentation
~~~~~~~~~~~~~~~~~~~

.. code:: bash

    # install requirements for documentation
    pip install -U -r requirements-docs.txt

    cd docs

    # generate html documentation
    make html

Then open ``docs/_build/html/index.html`` file in browser.
