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

        $ gauge run specs/

    .. _Gauge documentation: https://docs.getgauge.io/


Examples
~~~~~~~~

- **Selenium**: This project serves as an example for writing automation using Gauge. It uses selenium and various Gauge/Gauge-Python features. For more details, Check out the gauge-example-python_ repository.

.. _gauge-example-python: https://github.com/kashishm/gauge-example-python

- **Selenium and REST API**: This project shows an example of how to setup Gauge, Gauge Python and Magento_ to test REST API. For more details, Check out the blog_ or gauge-magento-test_ repository.

.. _Selenium and REST API: https://angbaird.com/2016/11/09/selenium-and-rest-api-testing-with-gauge/
.. _gauge-magento-test: https://github.com/angb/gauge-magento-test
.. _blog: https://angbaird.com/2016/11/09/selenium-and-rest-api-testing-with-gauge/
.. _Magento: https://magento.com/
