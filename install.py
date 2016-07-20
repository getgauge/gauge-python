# /usr/bin/env python
import json
import os
import shutil
import sys
from subprocess import call

cwd = os.getcwd()

PLUGIN_FILE_TEMPLATE = 'gauge-python-{}'

ZIP = 'zip'

VERSION = 'version'

PLUGIN_JSON = 'python.json'

BIN = os.path.join(cwd, 'bin')

DEPLOY = os.path.join(cwd, 'deploy')


def install():
    plugin_zip = create_zip()
    call(['gauge', '--uninstall', 'python', '--plugin-version', get_version()])
    exit_code = call(['gauge', '--install', 'python', '-f', os.path.join(BIN, plugin_zip)])
    shutil.rmtree('dist', True)
    print('Creating getgauge package.')
    fnull = open(os.devnull, 'w')
    call(['python', 'setup.py', 'sdist'], stdout=fnull, stderr=fnull)
    fnull.close()
    print('Install getgauge package using pip: \n\tpip install dist/*')
    sys.exit(exit_code)


def create_zip():
    wd = cwd
    if os.path.exists(DEPLOY):
        shutil.rmtree(DEPLOY)
    copy_files(wd)
    output_file = PLUGIN_FILE_TEMPLATE.format(get_version())
    shutil.make_archive(output_file, ZIP, DEPLOY)
    shutil.rmtree(DEPLOY)
    if os.path.exists(BIN):
        shutil.rmtree(BIN)
    os.mkdir(BIN)
    plugin_zip = '{0}.zip'.format(output_file)
    shutil.move(plugin_zip, BIN)
    print('Zip file created.')
    return plugin_zip


def get_version():
    json_data = open(PLUGIN_JSON).read()
    data = json.loads(json_data)
    return data[VERSION]


def copy_files(wd):
    copy(os.path.join(wd, 'skel'), os.path.join(DEPLOY, 'skel'))
    copy(os.path.join(wd, PLUGIN_JSON), DEPLOY)
    copy(os.path.join(wd, 'start.py'), DEPLOY)
    copy(os.path.join(wd, 'start.sh'), DEPLOY)
    copy(os.path.join(wd, 'start.bat'), DEPLOY)


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError:
        shutil.copy(src, dest)


def main():
    exit_code = call(['coverage', 'run', '--source', 'getgauge', '-m', 'unittest', 'discover'])
    if exit_code != 0:
        sys.exit(exit_code)
    if len(sys.argv) == 1:
        create_zip()
    elif sys.argv[1] == '--install':
        install()


main()
