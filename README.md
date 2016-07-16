# Gauge Python [![Documentation Status](https://readthedocs.org/projects/gauge-python/badge/?version=latest)](http://gauge-python.readthedocs.org/en/latest/?badge=latest) [![Build Status](https://snap-ci.com/kashishm/gauge-python/branch/master/build_image)](https://snap-ci.com/kashishm/gauge-python/branch/master) [![Build Status](https://travis-ci.org/kashishm/gauge-python.svg?branch=master)](https://travis-ci.org/kashishm/gauge-python)

Python language runner for __[Gauge](https://github.com/getgauge/gauge)__. Read the __[Documentation](https://gauge-python.readthedocs.org)__ for more details.


## Build from source
###Requirements
* Python
* Pip
* Gauge

### Installing package dependencies
```
pip install -r requirements.txt
```

### Tests
```
python install.py --test
```

### Tests Coverage
```
python install.py --test
coverage report -m
```

###Installing

````
python install.py --install
````

###Creating distributable

````
python install.py
````
This will create a .zip file in bin directory which can then be uploaded to Github releases.

##Uploading to PyPI

```
python setup.py sdist
twine upload dist/*
```
### License

The Gauge-Python is an open-sourced software licensed under the [MIT license](http://opensource.org/licenses/MIT).
