import importlib
import json
import py_compile
import shutil
import sys
import traceback
from os import path

from colorama import Fore
from colorama import Style

from getgauge.util import *

project_root = get_project_root()
impl_dir = get_step_impl_dir()
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
        print(Fore.RED + 'Cannot import step implementations. Error: {} does not exist.'.format(step_impl_dir))
        print(Fore.RED + 'Make sure `STEP_IMPL_DIR` env var is set to a valid directory path.')
        return
    _import_impl(step_impl_dir)


def copy_skel_files():
    try:
        print(Style.BRIGHT + 'Initialising Gauge Python project')
        print(Fore.GREEN + 'create  {}'.format(env_dir))
        os.makedirs(env_dir)
        print(Fore.GREEN + 'create  {}'.format(impl_dir))
        shutil.copytree(os.path.join(SKEL, STEP_IMPL_DIR_NAME), impl_dir)
        print(Fore.GREEN + 'create  {}'.format(os.path.join(env_dir, PYTHON_PROPERTIES)))
        shutil.copy(os.path.join(SKEL, PYTHON_PROPERTIES), env_dir)
        open(requirements_file, 'w').write('getgauge==' + _get_version())
    except:
        print(Fore.RED + 'Exception occurred while copying skel files.\n{}.'.format(traceback.format_exc()))
        sys.exit(1)


def _import_impl(step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            _import_file(file_path)
        elif path.isdir(file_path):
            load_impls(file_path)


def _import_file(file_path):
    rel_path = os.path.normpath(file_path.replace(project_root + os.path.sep, ''))
    try:
        py_compile.compile(file_path)
        importlib.import_module(os.path.splitext(rel_path.replace(os.path.sep, '.'))[0])
    except:
        print(Fore.RED + 'Exception occurred while loading step implementations from file: {}.'.format(rel_path))
        print(Fore.RED + traceback.format_exc())


def _get_version():
    json_data = open(PLUGIN_JSON).read()
    data = json.loads(json_data)
    return data[VERSION]
