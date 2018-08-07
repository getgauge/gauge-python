# Gauge-Python

[![Build Status](https://travis-ci.org/getgauge/gauge-python.svg?branch=master)](https://travis-ci.org/getgauge/gauge-python)
[![Build status](https://ci.appveyor.com/api/projects/status/ltbeao568cmyx566/branch/master?svg=true)](https://ci.appveyor.com/project/getgauge/gauge-python/branch/master)

This project adds Python [language plugin](https://docs.gauge.org/plugins.html#language-reporting-plugins) for [gauge](http://getgauge.io).

## Getting started

### Pre-requisite

- [Gauge](https://gauge.org/index.html)
- [Python](https://www.python.org/)
- [Pip](https://pip.pypa.io/en/stable/)

### Installation

```
gauge install python
```

### Create a gauge-python project

```
gauge init python
```

### Run tests

```
gauge run specs
```

### Useful links

- [User Docs](https://docs.gauge.org)
- [Setup Guide](https://gauge-python.readthedocs.io/en/latest/contributing.html#development-guide)

### Alternate Installation options

#### Install specific version
```
gauge install python -v 0.2.3
[pip / pip3] install getgauge
```

### Offline installation
* Download the plugin from [Releases](https://github.com/getgauge/gauge-python/releases)
```
gauge install python --file gauge-python-0.2.3.zip
[pip / pip3] install getgauge
```

#### Nightly installation
To install python nightly, download the latest nightly from [here](https://bintray.com/gauge/gauge-python/Nightly).

Once you have the downloaded nightly gauge-python-$VERSION.nightly-yyyy-mm-dd.zip, install using:

```
gauge install python -f gauge-python-$VERSION.nightly.yyyy-mm-dd.zip
[pip / pip3] install --pre getgauge==$VERSION.dev.yyyymmdd
```

#### Build from Source

##### Pre-Requisites

* [Golang](http://golang.org/)

##### Installing package dependencies
```
pip install -r requirements.txt
```

##### Tests
```
python build.py --test
```

##### Tests Coverage
```
python build.py --test
coverage report -m
```

##### Installing
```
python build.py --install
```

##### Creating distributable
```
python build.py --dist
```

This will create a .zip file in bin directory and a .tar.gz file in dist directory. The zip file can be uploaded to Github release and the .tar.gz file can be uploaded to PyPi

##### Uploading to PyPI
```
twine upload dist/FILE_NAME
```

##### Creating Nightly distributable
```
NIGHTLY=true python build.py --dist
```

This will create the .zip nightly file and a .dev.DATE.tar.gz(PyPi pre release package) file.

## Examples

- Selenium: This project serves as an example for writing automation using Gauge. It uses selenium and various Gauge/Gauge-Python features. For more details, Check out the [gauge-example-python](https://github.com/kashishm/gauge-example-python) repository.

- Selenium and REST API: This project shows an example of how to setup Gauge, Gauge Python and [Magento](https://magento.com/) to test REST API. For more details, Check out the [blog](https://angbaird.com/2016/11/09/selenium-and-rest-api-testing-with-gauge/) or [gauge-magento-test](https://github.com/angb/gauge-magento-test) repository.


## License

The Gauge-Python is an open-sourced software licensed under the `MIT license`.

## Copyright

Copyright 2018 ThoughtWorks, Inc.
