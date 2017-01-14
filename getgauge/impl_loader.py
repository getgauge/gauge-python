import importlib
import json
import os
import py_compile
import shutil
import sys
import traceback
from os import path

from colorama import Fore
from colorama import Style

PROJECT_ROOT_ENV = 'GAUGE_PROJECT_ROOT'
STEP_IMPL_DIR_ENV = 'STEP_IMPL_DIR'

STEP_IMPL_DIR = os.getenv(STEP_IMPL_DIR_ENV) or 'step_impl'
project_root = os.path.abspath(os.environ[PROJECT_ROOT_ENV])
impl_dir = os.path.join(project_root, STEP_IMPL_DIR)
env_dir = os.path.join(project_root, 'env', 'default')
requirements_file = os.path.join(project_root, 'requirements.txt')
sys.path.append(project_root)
PLUGIN_JSON = 'python.json'
VERSION = 'version'
PYTHON_PROPERTIES = 'python.properties'
SKEL = 'skel'


def load_impls(step_impl_dir=impl_dir):
    os.chdir(project_root)
    if not os.path.isdir(step_impl_dir):
        print(Fore.RED + 'Cannot import step implementations. Error: directory {} does not exist.'.format(step_impl_dir))
        print(Fore.RED + 'Make sure `STEP_IMPL_DIR` env var is set to a valid directory path.')
        return
    import_impl(step_impl_dir)


def import_impl(step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            import_file(file_path)
        elif path.isdir(file_path):
            load_impls(file_path)


def import_file(file_path):
    rel_path = os.path.normpath(file_path.replace(project_root + os.path.sep, ''))
    try:
        py_compile.compile(file_path)
        importlib.import_module(os.path.splitext(rel_path.replace(os.path.sep, '.'))[0])
    except:
        print(Fore.RED + 'Exception occurred while loading step implementations from file: {}.'.format(rel_path))
        print(Fore.RED + traceback.format_exc())


def copy_skel_files():
    try:
        print(Style.BRIGHT + 'Initialising Gauge Python project')
        print(Fore.GREEN + 'create  {}'.format(env_dir))
        os.makedirs(env_dir)
        print(Fore.GREEN + 'create  {}'.format(impl_dir))
        shutil.copytree(os.path.join(SKEL, STEP_IMPL_DIR), impl_dir)
        print(Fore.GREEN + 'create  {}'.format(os.path.join(env_dir, PYTHON_PROPERTIES)))
        shutil.copy(os.path.join(SKEL, PYTHON_PROPERTIES), env_dir)
        open(requirements_file, 'w').write('getgauge==' + get_version())
    except:
        print(Fore.RED + 'Exception occurred while copying skel files.\n{}.'.format(traceback.format_exc()))
        sys.exit(1)


def get_version():
    json_data = open(PLUGIN_JSON).read()
    data = json.loads(json_data)
    return data[VERSION]
