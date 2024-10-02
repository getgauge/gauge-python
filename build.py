# /usr/bin/env python

import glob
import json
import os
import shutil
import sys
from pathlib import Path
from subprocess import call

cwd = os.getcwd()

PLUGIN_FILE_TEMPLATE = 'gauge-python-{}'

ZIP = 'zip'

VERSION = 'version'

PLUGIN_JSON = 'python.json'

BIN = os.path.join(cwd, 'bin')

DEPLOY = os.path.join(cwd, 'deploy')

ROOT_DIR = Path(__file__).resolve().parent


def install():
    plugin_zip = create_zip()
    call(['gauge', 'uninstall', 'python', '-v', get_version()])
    exit_code = call(['gauge', 'install', 'python', '-f',
                      os.path.join(BIN, plugin_zip)])
    generate_package()
    p = os.listdir("dist")[0]
    print(f"Installing getgauge package using pip: \n\tpip install dist/{p}")
    call([sys.executable, "-m", "pip", "install",
         f"dist/{p}", "--upgrade", "--user"])
    sys.exit(exit_code)


def create_setup_file():
    with open("setup.tmpl", "r", encoding="utf-8") as tmpl:
        tmpl_content = tmpl.read()
    with open("setup.py", "w+", encoding="utf-8") as setup:
        v = get_version()
        setup.write(tmpl_content.format(v))


def generate_package():
    shutil.rmtree('dist', True)
    print('Creating getgauge package.')
    create_setup_file()
    with open(os.devnull, 'w', encoding="utf-8") as fnull:
        call([sys.executable, 'setup.py', 'sdist'], stdout=fnull, stderr=fnull)


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
    plugin_zip = f"{output_file}.zip"
    shutil.move(plugin_zip, BIN)
    print('Zip file created.')
    return plugin_zip


def get_version():
    with open(PLUGIN_JSON, "r", encoding="utf-8") as json_data:
        data = json.loads(json_data.read())
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
Usage: python build.py --[option]

Options:
    --test    :     runs unit tests.
    --install :     installs python plugin and generates the pip package
"""


def run_tests() -> int:
    pp = "PYTHONPATH"
    os.environ[pp] = str(ROOT_DIR)
    exit_code = 0
    all_python_test_files = glob.glob(f"{ROOT_DIR}/tests/**/test_*.py", recursive=True)
    for i, file_name_path in enumerate(all_python_test_files):
        command = ["coverage", "run", file_name_path]
        exit_code = call(command) if exit_code == 0 else exit_code
        # Keep coverage files
        os.rename(".coverage", f".coverage.{i}")
    call(["coverage", "combine"])
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
