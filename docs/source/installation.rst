.. _installation:

Installation
------------


-  Before installing gauge-python, make sure Gauge ``v0.3.0`` or above is installed

   .. code:: sh

       $ gauge -v

.. note::
   ``getgauge`` package supports ``python2.7`` and ``python3.*``.


Online Installation
~~~~~~~~~~~~~~~~~~~

-  Run the following commands to install gauge-python

   ::

        $ gauge install python
        $ [pip / pip3] install getgauge

-  Installing specific version

   ::

       $ gauge install python -v 0.2.3
       $ [pip / pip3] install getgauge

Offline Installation
~~~~~~~~~~~~~~~~~~~~
- Download the plugin from Releases_

    .. _Releases: https://github.com/getgauge/gauge-python/releases

- Run the following command to install from the downloaded file

   ::

       $ gauge install python -f gauge-python-0.2.3.zip
       $ [pip / pip3] install getgauge



Verify installation
~~~~~~~~~~~~~~~~~~~

- Run the following command and plugin ``python`` should be listed in the plugin section.

   ::

       $ gauge -v


       Gauge version: 0.9.7

       Plugins
       -------
       html-report (2.1.1)
       python (0.2.4)


- To verify ``getgauge`` package is installed, run the following command and the output should contain package details.

   ::

        $ pip/pip3 show getgauge

        ---
        Metadata-Version: 1.1
        Name: getgauge
        Version: 0.2.4
        Summary: Enables Python support for Gauge
        Home-page: https://github.com/getgauge/gauge-python
        Author: Gauge Team
        Author-email: getgauge@outlook.com
        License: MIT
        Location: /usr/local/lib/python3.5/site-packages
        Requires: protobuf, redBaron


Nightly Installation
~~~~~~~~~~~~~~~~~~~~
- Download the plugin from Noghtly Releases_

    .. _Releases: https://bintray.com/gauge/gauge-python/Nightly

- Run the following command to install from the downloaded file

   ::

       $ gauge install python -f gauge-python-$VERSION.nightly.$NIGHTLY_DATE.zip
       $ [pip / pip3] install --pre getgauge==getgauge.$VERSION.dev.$NIGHTLY_DATE_WITHOUT_ANY_SEPARATOR


- Example
   ::

       $ gauge install python -f gauge-python-0.2.4.nightly.2018-02-08.zip
       $ [pip / pip3] install --pre getgauge==getgauge.0.2.4.dev.20180208

Verify Nightly installation
~~~~~~~~~~~~~~~~~~~

- Run the following command and plugin ``python`` should be listed in the plugin section.

   ::

       $ gauge -v


       Gauge version: 0.9.8

       Plugins
       -------
       html-report (2.1.1)
       python (0.2.4)


- To verify ``getgauge`` package is installed, run the following command and the output should contain package details.

   ::

        $ pip/pip3 show getgauge

        ---
        Metadata-Version: 1.1
        Name: getgauge
        Version: 0.2.4.dev.20180208
        Summary: Enables Python support for Gauge
        Home-page: https://github.com/getgauge/gauge-python
        Author: Gauge Team
        Author-email: getgauge@outlook.com
        License: MIT
        Location: /usr/local/lib/python3.5/site-packages
        Requires: protobuf, redBaron

