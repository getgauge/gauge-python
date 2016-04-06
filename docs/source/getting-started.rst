.. _getting-started:

Getting Started
---------------

If you are new to Gauge, please consult the `Gauge documentation`_ to know about how Gauge works.

Initialization
~~~~~~~~~~~~~~

To initialize a project with gauge-python, in an empty directory run:

    .. code:: sh

        $ gauge --init python

    The project structure should look like this:

       ::

            ├── env
            │   └── default
            │       └── default.properties
            |
            ├── logs
            |
            ├── specs
            │   └── example.spec
            |
            ├── step_impl
            │   └── step_impl.py
            |
            ├── manifest.json


Execution
~~~~~~~~~

To execute a gauge-python project, run the following command in the project:

    .. code:: sh

        $ gauge specs/

    .. _Gauge documentation: http://getgauge.io/documentation/user/current/


Examples
~~~~~~~~

- gauge-example-python_: This project serves as an example for writing Automation using Gauge. It uses selenium and various Gauge/Gauge-Python features. For more details, Check out the repository_.

.. _gauge-example-python: https://github.com/kashishm/gauge-example-python
.. _repository: https://github.com/kashishm/gauge-example-python