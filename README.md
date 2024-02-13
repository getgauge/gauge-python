# Gauge-Python

[![Actions Status](https://github.com/getgauge/gauge-python/actions/workflows/tests.yml/badge.svg)](https://github.com/getgauge/gauge-python/actions)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v1.4%20adopted-ff69b4.svg)](CODE_OF_CONDUCT.md)

This project adds Python [language plugin](https://docs.gauge.org/plugins.html#language-reporting-plugins) for [gauge](http://gauge.org).

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

This will create a .zip file in bin directory and a .tar.gz file in dist directory.

## Deployment

Only contributors with push access can create a deployment.

The deployment process is managed via Github Actions.

Follow these steps to deploy gauge-python.

* Create a Personal Access Token in Github with `repo:public_repo` scope (skip this step if you already have a PAT).
* Run `GITHUB_TOKEN={Your token} sh release.sh` in `gauge-python` dir. This will trigger a deployment workflow on Github Actions. This workflow creates a release draft with all required assets and information.
* Visit to the release draft, analyze and update the contents (remove unnecessary entries, mention Contributors, remove dependabot PR entries).
* Publish the draft release.
* Once the draft is published it will trigger another workflow on Github Actions, which will perform all the Post release tasks, In case of gauge-python it will upload the `getgauge` python packge to `PyPi`.
* Once it's done please update the new release information in [gauge-repository](https://github.com/getgauge/gauge-repository/blob/master/python-install.json)
* That's it. Now the release can be announced on the required community platforms (chat, google group etc.)


## Examples

- Selenium: This project serves as an example for writing automation using Gauge. It uses selenium and various Gauge/Gauge-Python features. For more details, Check out the [gauge-example-python](https://github.com/getgauge-examples/python-selenium) repository.

- Selenium and REST API: This project shows an example of how to setup Gauge, Gauge Python and [Magento](https://magento.com/) to test REST API. For more details, Check out the [blog](https://angbaird.com/2016/11/09/selenium-and-rest-api-testing-with-gauge/) or [gauge-magento-test](https://github.com/angb/gauge-magento-test) repository.


## License

The Gauge-Python is an open-sourced software licensed under the `MIT license`.

## Copyright

Copyright 2018 ThoughtWorks, Inc.
