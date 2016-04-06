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
