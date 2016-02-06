# /usr/bin/env python
import errno
import json
import os
import shutil
import sys
from subprocess import call

CWD = os.getcwd()

PLUGIN_FILE_TEMPLATE = 'gauge-python-{}'

ZIP = 'zip'

VERSION = 'version'

plugin_json = "python.json"

BIN = os.path.join(CWD, "bin")

DEPLOY = os.path.join(CWD, "deploy")


def install():
    plugin_zip = create_zip()
    call(["gauge", "--uninstall", "python", "--plugin-version", get_version()])
    exit_code = call(["gauge", "--install", "python", "-f", os.path.join(BIN, plugin_zip)])
    sys.exit(exit_code)


def create_zip():
    wd = CWD
    if os.path.exists(DEPLOY):
        shutil.rmtree(DEPLOY)
    copy_files(wd)
    output_file = PLUGIN_FILE_TEMPLATE.format(get_version())
    shutil.make_archive(output_file, ZIP, DEPLOY)
    shutil.rmtree(DEPLOY)
    if os.path.exists(BIN):
        shutil.rmtree(BIN)
    os.mkdir(BIN)
    plugin_zip = "{0}.zip".format(output_file)
    shutil.move(plugin_zip, BIN)
    print("Zip file created.")
    return plugin_zip


def get_version():
    json_data = open(plugin_json).read()
    data = json.loads(json_data)
    return data[VERSION]


def copy_files(wd):
    copy(os.path.join(wd, "step_impl"), os.path.join(DEPLOY, "step_impl"))
    copy(os.path.join(wd, plugin_json), DEPLOY)
    copy(os.path.join(wd, "start.py"), DEPLOY)
    copy(os.path.join(wd, "start.bat"), DEPLOY)


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError:
        shutil.copy(src, dest)


def main():
    exit_code = call(["coverage", "run", "--source", "getgauge", "-m", "unittest", "discover"])
    if exit_code != 0:
        return
    if len(sys.argv) == 1:
        create_zip()
    elif sys.argv[1] == '--install':
        install()


main()
