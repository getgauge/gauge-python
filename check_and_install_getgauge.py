import subprocess
import sys
import os
import pkg_resources
from distutils import version
from subprocess import Popen, PIPE
import json


def get_version():
    proc = Popen("gauge -v --machine-readable",
                 stdout=PIPE, stderr=PIPE, shell=True)
    out, _ = proc.communicate()
    data = json.loads(str(out.decode()))
    for plugin in data['plugins']:
        if plugin['name'] == 'python':
            return plugin['version']
    return ''


def get_dev_getgauge_version(plugin_nightly_version):
    refined_version = plugin_nightly_version.replace(
        'nightly', '').replace('-', '')
    return refined_version[:6] + "dev" + refined_version[6:]


def install_getgauge(getgauge_version):
    if "dev" in getgauge_version:
        subprocess.call([sys.executable, "-m", "pip", "install", "--pre",
                         getgauge_version, "--user"], stdout=open(os.devnull, 'wb'))
    else:
        subprocess.call([sys.executable, "-m", "pip", "install",
                         getgauge_version, "--user"], stdout=open(os.devnull, 'wb'))


def assert_versions():
    python_plugin_version = get_version()
    expected_gauge_version = python_plugin_version

    if "nightly" in python_plugin_version:
        expected_gauge_version = get_dev_getgauge_version(
            python_plugin_version)

    try:
        getgauge_version = pkg_resources.get_distribution('getgauge').version
        if getgauge_version is not expected_gauge_version:
            install_getgauge("getgauge=="+expected_gauge_version)
    except pkg_resources.DistributionNotFound:
        install_getgauge("getgauge=="+expected_gauge_version)


if __name__ == '__main__':
    assert_versions()
