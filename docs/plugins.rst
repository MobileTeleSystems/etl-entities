.. _plugins:

Plugins
=======

What are plugins?
-----------------

Terms
~~~~~
* ``Plugin`` - some Python package which implements some extra functionality for etl_entities
* ``Plugin autoimport`` - etl_entities behavior which allows to automatically import this package if it contains proper metadata (``entry_points``)

Features
~~~~~~~~

Plugins mechanism allows to:

* Automatically register new classes, like HWM type, HWM stores and so on

Limitations
~~~~~~~~~~~
Unlike other projects (like *Airflow 1.x*), plugins does not inject imported classes or functions to ``etl_entities.*`` namespace.
Users should import classes from the plugin package **explicitly** to avoid name collisions.

How to implement plugin?
------------------------

Create a Python package ``some-plugin`` with a file ``some_plugin/setup.py``:

.. code-block:: python

    # some_plugin/setup.py
    from setuptools import setup

    setup(
        # if you want to import something from etl_entities, add it to requirements list
        install_requires=["etl_entities"],
        entry_points={
            # this key enables plugins autoimport functionality
            "etl_entities.plugins": [
                "some-plugin-name=some_plugin.module",  # automatically import all module content
                "some-plugin-class=some_plugin.module.internals:MyClass",  # import a specific class
                "some-plugin-function=some_plugin.module.internals:my_function",  # import a specific function
            ],
        },
    )

See `setuptools documentation for entry_points <https://setuptools.pypa.io/en/latest/userguide/entry_point.html>`_


How plugins are imported?
-------------------------

* User should install a package implementing the plugin:

.. code-block:: bash

    pip install some-package

* Then user should import something from ``etl_entities`` module or its submodules:

.. code-block:: python

    import etl_entities
    from etl_entities.hwm import ColumnIntHWM

    # and so on

* This import automatically executes something like:

.. code-block:: python

    import some_plugin.module
    from some_plugin.module.internals import MyClass
    from some_plugin.module.internals import my_function

If specific module/class/function uses some registration capabilities of etl_entities,
like :ref:`hook-decorator`, it will be executed during this import.

How to enable/disable plugins?
------------------------------

Disable/enable all plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default plugins are enabled.

To disabled them, you can set environment variable ``ETL_ENTITIES_PLUGINS_ENABLED`` to ``false`` BEFORE
importing etl_entities. This will disable all plugins autoimport.

But user is still be able to explicitly import ``some_plugin.module``, executing
all decorators and registration capabilities of etl_entities.

Disable a specific plugin (blacklist)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If some plugin is failing during import, you can disable it by setting up environment variable
``ETL_ENTITIES_PLUGINS_BLACKLIST=some-failing-plugin``. Multiple plugin names could be passed with ``,`` as delimiter.

Again, this environment variable should be set BEFORE importing etl_entities.

Disable all plugins except a specific one (whitelist)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also disable all plugins except a specific one by setting up environment variable
``ETL_ENTITIES_PLUGINS_WHITELIST=some-not-failing-plugin``. Multiple plugin names could be passed with ``,`` as delimiter.

Again, this environment variable should be set BEFORE importing etl_entities.

If both whitelist and blacklist environment variables are set, blacklist has a higher priority.


How to see logs of the plugins mechanism?
-----------------------------------------

Plugins registration emits logs with ``INFO`` level:

.. code:: python

    import logging

    logging.basicConfig(level=logging.INFO)

.. code-block:: text

    INFO   Found 2 plugins
    INFO   Loading plugin 'my-plugin'
    INFO   Skipping plugin 'failing' because it is in a blacklist

More detailed logs are emitted with ``DEBUG`` level, to make output less verbose:

.. code:: python

    import logging

    logging.basicConfig(level=logging.DEBUG)

.. code-block:: text

    DEBUG  Searching for plugins with group 'etl_entities.plugins'
    DEBUG  |Plugins| Plugins whitelist: []
    DEBUG  |Plugins| Plugins blacklist: ['failing-plugin']
    INFO   |Plugins| Found 2 plugins
    INFO   Loading plugin (1/2):
    DEBUG      name: 'my-plugin'
    DEBUG      package: 'my-package'
    DEBUG      version: '0.1.0'
    DEBUG      importing: 'my_package.my_module:MyClass'
    DEBUG  Successfully loaded plugin 'my-plugin'
    DEBUG      source: '/usr/lib/python3.11/site-packages/my_package/my_module/my_class.py'
    INFO   Skipping plugin 'failing' because it is in a blacklist
