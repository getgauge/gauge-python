# /usr/bin/env python
import json
import os
import shutil
import sys
from datetime import date
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
    call(['gauge', 'uninstall', 'python', '-v', get_version()])
    exit_code = call(['gauge', 'install', 'python', '-f', os.path.join(BIN, plugin_zip)])
    generate_package()
    p = os.listdir("dist")[0]
    print("Installing getgauge package using pip: \n\tpip install dist/{}".format(p))
    call([sys.executable, "-m", "pip", "install", "dist/{}".format(p), "--upgrade", "--user"])
    sys.exit(exit_code)


def create_setup_file():
    tmpl = open("setup.tmpl", "r")
    setup = open("setup.py", "w+")
    v = get_version()
    setup.write(tmpl.read().format(v, "{\n\t\t':python_version == \"2.7\"': ['futures']\n\t}"))
    setup.close()
    tmpl.close()


def generate_package():
    shutil.rmtree('dist', True)
    print('Creating getgauge package.')
    create_setup_file()
    fnull = open(os.devnull, 'w')
    call([sys.executable, 'setup.py', 'sdist'], stdout=fnull, stderr=fnull)
    fnull.close()


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
    copy(os.path.join(wd, 'check_and_install_getgauge.py'), DEPLOY)
    copy(os.path.join(wd, 'start.py'), DEPLOY)
    copy(os.path.join(wd, 'start.sh'), DEPLOY)
    copy(os.path.join(wd, 'start.bat'), DEPLOY)


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError:
        shutil.copy(src, dest)


usage = """
Usage: python install.py --[option]

Options:
    --test    :     runs unit tests.
    --install :     installs python plugin and generates the pip package
"""


def run_tests():
    pp = "PYTHONPATH"
    os.environ[pp] = "{0}{1}{2}".format( os.environ.get(pp), os.pathsep, os.path.abspath(os.path.curdir))
    test_dir = os.path.join(os.path.curdir, "tests")
    exit_code = 0
    for root, _, files in os.walk(test_dir):
        for item in files:
            if item.startswith("test_") and item.endswith(".py"):
                fileNamePath = str(os.path.join(root, item))
                exit_code = call([sys.executable, fileNamePath]
                                 ) if exit_code is 0 else exit_code
    return exit_code


def main():
    if len(sys.argv) < 2:
        print(usage)
    else:
        if sys.argv[1] == '--dist':
            create_zip()
            generate_package()
        else:
            exit_code = run_tests()
            if exit_code != 0:
                sys.exit(exit_code)
            elif sys.argv[1] == '--install':
                install()



if __name__ == '__main__':
    main()
