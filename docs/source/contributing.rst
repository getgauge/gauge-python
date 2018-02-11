.. _contributing:

Contributing
------------

Issues
~~~~~~

If you find any issues or have any feature requests, please file them in the `issue tracker`_.

.. _issue tracker: https://github.com/getgauge/gauge-python/issues


If you are filing issues, please provide the version of gauge core, python, gauge-python plugin and getgauge package that you have installed. You can find it by running following commands

   ::

        $ gauge -v
        $ python --version
        $ pip show getgauge


Documentation
~~~~~~~~~~~~~

You can enhance the documentation. The code for documentation is present on Github_. It uses Sphinx_ and it is written in reStructuredText.
It's free and simple. Read the `Getting Started`_ guide to get going!

.. _Github: https://github.com/getgauge/gauge-python/tree/master/docs/source
.. _Sphinx: http://www.sphinx-doc.org/
.. _Getting Started: https://read-the-docs.readthedocs.org/en/latest/getting_started.html


Pull Requests
~~~~~~~~~~~~~
Contributions to Gauge-Python are welcome and appreciated. Implement features, fix bugs and send us pull requests.

Development Guide
^^^^^^^^^^^^^^^^^

Requirements
""""""""""""

-  Python
-  Pip
-  Gauge

Installing package dependencies
"""""""""""""""""""""""""""""""

::

    pip install -r requirements.txt

Tests
"""""

::

    python build.py --test

Tests Coverage
""""""""""""""

::

    python build.py --test
    coverage report -m

Installing
""""""""""

::

    python build.py --install

Creating distributable
""""""""""""""""""""""

::

    python build.py --dist

This will create a .zip file in bin directory and a .tar.gz file in dist directory.
The zip file can be uploaded to Github release and the .tar.gz file can be uploaded to PyPi

Uploading to PyPI
"""""""""""""""""

::

    twine upload dist/FILE_NAME

Creating Nightly distributable
""""""""""""""""""""""

::

    NIGHTLY=true python build.py --dist

This will create the .zip nightly file and a .dev.DATE.tar.gz(PyPi pre release package) file.
