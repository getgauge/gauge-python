import importlib
import inspect
import json
import os
import re
import shutil
import sys
import traceback
from contextlib import contextmanager
from os import path

from getgauge import logger
from getgauge.registry import registry
from getgauge.util import get_project_root, get_step_impl_dirs

project_root = get_project_root()
impl_dirs = get_step_impl_dirs()
env_dir = os.path.join(project_root, 'env', 'default')
requirements_file = os.path.join(project_root, 'requirements.txt')
sys.path.append(project_root)
temporary_sys_path = []
PLUGIN_JSON = 'python.json'
VERSION = 'version'
PYTHON_PROPERTIES = 'python.properties'
SKEL = 'skel'


def load_impls(step_impl_dirs=impl_dirs):
    os.chdir(project_root)
    for impl_dir in step_impl_dirs:
        if not os.path.isdir(impl_dir):
            logger.error('Cannot import step implementations. Error: {} does not exist.'.format(step_impl_dirs))
            logger.error('Make sure `STEP_IMPL_DIR` env var is set to a valid directory path.')
            return
        base_dir = project_root if impl_dir.startswith(project_root) else os.path.dirname(impl_dir)
        # Handle multi-level relative imports
        for _ in range(impl_dir.count('..')):
            base_dir = os.path.dirname(base_dir).replace("/", os.path.sep).replace("\\", os.path.sep)
        # Add temporary sys path for relative imports that is not already added
        if '..' in impl_dir and base_dir not in temporary_sys_path:
            temporary_sys_path.append(base_dir)
        _import_impl(base_dir, impl_dir)


def copy_skel_files():
    try:
        logger.info('Initialising Gauge Python project')
        logger.info('create  {}'.format(env_dir))
        os.makedirs(env_dir)
        logger.info('create  {}'.format(impl_dirs[0]))
        shutil.copytree(os.path.join(SKEL,path.basename(impl_dirs[0]) ), impl_dirs[0])
        logger.info('create  {}'.format(os.path.join(env_dir, PYTHON_PROPERTIES)))
        shutil.copy(os.path.join(SKEL, PYTHON_PROPERTIES), env_dir)
        with open(requirements_file, 'w', encoding="utf-8") as f:
            f.write('getgauge==' + _get_version())
    except:
        logger.fatal('Exception occurred while copying skel files.\n{}.'.format(traceback.format_exc()))


def _import_impl(base_dir, step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            _import_file(base_dir, file_path)
        elif path.isdir(file_path):
            _import_impl(base_dir, file_path)

@contextmanager
def use_temporary_sys_path():
    original_sys_path = sys.path[:]
    sys.path.extend(temporary_sys_path)
    try:
        yield
    finally:
        sys.path = original_sys_path

def _import_file(base_dir, file_path):
    rel_path = os.path.normpath(file_path.replace(base_dir + os.path.sep, ''))
    try:
        module_name = os.path.splitext(rel_path.replace(os.path.sep, '.'))[0]
        # Use temporary sys path for relative imports
        if '..' in file_path:
            with use_temporary_sys_path():
                m = importlib.import_module(module_name)
        else:
            m = importlib.import_module(module_name)
        # Get all classes in the imported module
        classes = inspect.getmembers(m, lambda member: inspect.isclass(member) and member.__module__ == module_name)
        if len(classes) > 0:
            for c in classes:
                file = inspect.getfile(c[1])
                # Create instance of step implementation class.
                if _has_methods_with_gauge_decoratores(c[1]):
                    update_step_registry_with_class(c[1](), file_path) # c[1]() will create a new instance of the class
    except:
        logger.fatal('Exception occurred while loading step implementations from file: {}.\n{}'.format(rel_path, traceback.format_exc()))

# Inject instance in each class method (hook/step)
def update_step_registry_with_class(instance, file_path):
    # Resolve the absolute path from relative path
    # Note: relative path syntax ".." can appear in between the file_path too like "<Project_Root>/../../Other_Project/src/step_impl/file.py"
    file_path = os.path.abspath(file_path) if ".." in str(file_path) else file_path
    method_list = registry.get_all_methods_in(file_path)
    for info in method_list:
        class_methods = [x[0] for x in inspect.getmembers(instance, inspect.ismethod)]
        if info.impl.__name__ in class_methods:
            info.instance = instance
    return method_list

def _get_version():
    with open(PLUGIN_JSON, "r", encoding="utf-8") as json_data:
        data = json.loads(json_data.read())
    return data[VERSION]

def _has_methods_with_gauge_decoratores(klass) -> bool:
    gauge_decorator_pattern = r"@(step|before_suite|after_suite|before_scenario|after_scenario|before_spec|after_spec|before_step|after_step|screenshot|custom_screen_grabber)"
    sourcelines = inspect.getsourcelines(klass)[0]
    for line in sourcelines:
        if re.match(gauge_decorator_pattern, line.strip()) is not None:
            return True
    return False
