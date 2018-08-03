.. _faq:

FAQ
---

ImportError: No module named getgauge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing the getgauge package using pip should fix this. You can install the package by running the following command

::

    [sudo] pip install getgauge


Failed to start gauge API: Plugin 'python' not installed on following locations : [PATH]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installing the gauge-python plugin should fix this. You can install the plugin by running the following command

::

    gauge --install python


Make sure you have the getgauge package. If you don't have, run the following command to install
::

    [sudo] pip install getgauge

For more details, refer Installation_ docs.

.. _Installation: ./installation.html


Change/Rename default step implementation(``step_impl``) directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create ``python.properties`` file in the ``<PROJECT_DIR>/env/default`` directory and add the following line to it.

::

    STEP_IMPL_DIR = PATH_TO_STEP_IMPLEMENTATION_DIR

.. note::
   The path specified in ``STEP_IMPL_DIR`` property should be relative to project root.


Use different version of python while running specs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default the language runner uses ``python`` command to run specs. To change the default behaviour, add ``GAUGE_PYTHON_COMMAND`` property to the ``python.properties`` file in the ``<PROJECT_DIR>/env/default`` directory.

::

    GAUGE_PYTHON_COMMAND = <python_command>
    GAUGE_PYTHON_COMMAND = python3
    GAUGE_PYTHON_COMMAND = python2

ImportError: No module named step_impl.<file_name>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This error happens on older versions of Python(2.7, 3.2). Create ``step_impl/__init__.py`` to fix this.


Steps not found or refactor failure after upgrading from 0.3.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have replaced the internal Python parsing engine after version 0.3.3 was released. This change was necessary to support Python 3 syntax. We have tried our best to make sure there is no user impact on users. However, you may have found a bug in our new parser.

To revert to the old parser implementation, add ``GETGAUGE_USE_0_3_3_PARSER`` property to the ``python.properties`` file in the ``<PROJECT_DIR>/env/default`` directory.

::
    GETGAUGE_USE_0_3_3_PARSER = true

If this fixes your issue (or if you are still encountering it); please create an issue in our GitHub Project. This property along with the old parser will be removed in future releases.
