import importlib
import inspect
import json
import re
import shutil
import sys
import traceback
from os import path

from getgauge import logger
from getgauge.registry import registry
from getgauge.util import *

project_root = get_project_root()
impl_dirs = get_step_impl_dirs()
env_dir = os.path.join(project_root, 'env', 'default')
requirements_file = os.path.join(project_root, 'requirements.txt')
sys.path.append(project_root)
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
        f = open(requirements_file, 'w')
        f.write('getgauge==' + _get_version())
        f.close()
    except:
        logger.fatal('Exception occurred while copying skel files.\n{}.'.format(traceback.format_exc()))


def _import_impl(base_dir, step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            _import_file(base_dir, file_path)
        elif path.isdir(file_path):
            _import_impl(base_dir, file_path)


def _import_file(base_dir, file_path):
    rel_path = os.path.normpath(file_path.replace(base_dir + os.path.sep, ''))
    try:
        module_name = os.path.splitext(rel_path.replace(os.path.sep, '.'))[0]
        m = importlib.import_module(module_name)
        # Get all classes in the imported module
        classes = inspect.getmembers(m, lambda member: inspect.isclass(member) and member.__module__ == module_name)
        if len(classes) > 0:
            for c in classes:
                file = inspect.getfile(c[1])
                # Create instance of step implementation class.
                if _has_methods_with_gauge_decoratores(c[1]):
                    update_step_resgistry_with_class(c[1](), file_path) # c[1]() will create a new instance of the class
    except:
        logger.error('Exception occurred while loading step implementations from file: {}.'.format(rel_path))
        logger.error(traceback.format_exc())

# Inject instace in each class method (hook/step)
def update_step_resgistry_with_class(instance, file_path):
    for info in registry.get_all_methods_in(file_path):
        class_methods = [x[0] for x in inspect.getmembers(instance, inspect.ismethod)]
        if info.impl.__name__ in class_methods:
            info.instance = instance


def _get_version():
    json_data = open(PLUGIN_JSON).read()
    data = json.loads(json_data)
    return data[VERSION]

def _has_methods_with_gauge_decoratores(klass):
    foo = r"@(step|before_suite|after_suite|before_scenario|after_scenario|before_spec|after_spec|before_step|after_step|screenshot|custom_screen_grabber)"
    sourcelines = inspect.getsourcelines(klass)[0]
    for i,line in enumerate(sourcelines):
        if re.match(foo, line.strip()) != None:
            return True
