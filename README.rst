Gauge Python |Documentation Status| |Snap Build Status| |Travis Build Status|
=============================================================================

Python language runner for `Gauge`_. Read the `Documentation`_
for more details.

Build from source
-----------------

Requirements
~~~~~~~~~~~~

-  Python
-  Pip
-  Gauge

Installing package dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install -r requirements.txt

Tests
~~~~~

::

    python install.py --test

Tests Coverage
~~~~~~~~~~~~~~

::

    python install.py --test
    coverage report -m

Installing
~~~~~~~~~~

::

    python install.py --install

Creating distributable
~~~~~~~~~~~~~~~~~~~~~~

::

    python install.py

This will create a .zip file in bin directory which can then be uploaded
to Github releases.

Uploading to PyPI
-----------------

::

    python setup.py sdist
    twine upload dist/*

License
~~~~~~~

The Gauge-Python is an open-sourced software licensed under the `MIT license`_.

.. _Gauge: https://github.com/getgauge/gauge
.. _Documentation: https://gauge-python.readthedocs.org
.. _MIT license: http://opensource.org/licenses/MIT

.. |Documentation Status| image:: https://readthedocs.org/projects/gauge-python/badge/?version=latest
   :target: http://gauge-python.readthedocs.org/en/latest/?badge=latest
.. |Snap Build Status| image:: https://snap-ci.com/kashishm/gauge-python/branch/master/build_image
   :target: https://snap-ci.com/kashishm/gauge-python/branch/master
.. |Travis Build Status| image:: https://travis-ci.org/kashishm/gauge-python.svg?branch=master
   :target: https://travis-ci.org/kashishm/gauge-python