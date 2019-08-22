import json
import sys
from subprocess import check_output

import pkg_resources


def get_version():
    out = check_output(["gauge -v --machine-readable"],shell=True)
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
    install_cmd = [sys.executable, "-m", "pip", "install", getgauge_version, "--user"]
    if "dev" in getgauge_version:
        install_cmd.append("--pre")
    check_output([" ".join(install_cmd)], shell=True)


def assert_versions():
    python_plugin_version = get_version()
    if not python_plugin_version:
        print('The gauge python plugin is not installed!')
        exit(1)

    expected_gauge_version = python_plugin_version
    if "nightly" in python_plugin_version:
        expected_gauge_version = get_dev_getgauge_version(
            python_plugin_version)

    try:
        getgauge_version = pkg_resources.get_distribution('getgauge').version
        if getgauge_version != expected_gauge_version:
            install_getgauge("getgauge=="+expected_gauge_version)
    except pkg_resources.DistributionNotFound:
        install_getgauge("getgauge=="+expected_gauge_version)


if __name__ == '__main__':
    assert_versions()
