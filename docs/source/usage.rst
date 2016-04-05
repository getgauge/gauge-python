.. _usage:

Usage
-----

If you are new to Gauge, please consult the `Gauge documentation`_ to know about how Gauge works.

**Initialize:** To initialize a project with gauge-python, in an empty directory run:

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


**Execute:**

    .. code:: sh

        $ gauge specs/

    .. _Gauge documentation: http://getgauge.io/documentation/user/current/