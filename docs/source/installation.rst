.. _installation:

Installation
------------


-  **Before installing gauge-python, make sure Gauge v0.3.0 or above is installed**

   .. code:: sh

       gauge -v

-  **Run the following commands to install gauge-python**

   ::

        gauge --install python
        pip install getgauge

-  **Installing specific version**

   ::

       gauge --install python --plugin-version 0.0.1
       pip install getgauge

-  **Offline installation** Download the plugin from Releases_
    .. _Releases: https://github.com/kashishm/gauge-python/releases

   ::

       gauge --install python --file gauge-python-0.0.1.zip
       pip install getgauge


.. note::
   For Python 3, use ``pip install getgauge>=0.1.0``

   For Python 2, use ``pip install getguage<=0.0.3``


-  **Verify installation**



   Run the following command and plugin ``python`` should be listed in the plugin section.
    ::

       gauge -v


       Gauge version: 0.4.0

            Plugins
            -------
            html-report (2.1.1)
            python (0.0.1)


   To verify ``getgauge`` package is installed, run the following command and the output should contain package details.
    ::

        pip show getgauge

        ---
        Metadata-Version: 1.1
        Name: getgauge
        Version: 0.0.1
        Summary: Enables Python support for Gauge
        Home-page: https://github.com/kashishm/gauge-python
        Author: Kashish Munjal
        Author-email: kashishmunjal64@gmail.com
        License: MIT
        Location: /usr/local/lib/python3.5/site-packages
        Requires: protobuf, redBaron

