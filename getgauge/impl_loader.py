import glob
import importlib
import inspect
import json
import os
import re
import shutil
import sys
import traceback
from contextlib import contextmanager
from importlib import util as importlib_util
from os import path
from pathlib import Path
from typing import Optional

from getgauge import logger
from getgauge.registry import registry
from getgauge.util import get_project_root, get_step_impl_dirs

project_root = get_project_root()
impl_dirs = get_step_impl_dirs()
env_dir = os.path.join(project_root, 'env', 'default')
requirements_file = os.path.join(project_root, 'requirements.txt')
sys.path.append(project_root)

PLUGIN_JSON = 'python.json'
VERSION = 'version'
PYTHON_PROPERTIES = 'python.properties'
SKEL = 'skel'


def load_impls(step_impl_dirs=impl_dirs, project_root=project_root):
    """ project_root can be overwritten in tests! """
    os.chdir(project_root)
    logger.debug('Project root: {}'.format(project_root))
    for impl_dir in step_impl_dirs:
        resolved_impl_dir = Path(impl_dir).resolve()
        if not resolved_impl_dir.is_dir():
            logger.error('Cannot import step implementations. Error: {} does not exist.'.format(impl_dir))
            logger.error('Make sure `STEP_IMPL_DIR` env var is set to a valid directory path.')
            return

        base_dir = project_root if str(resolved_impl_dir).startswith(project_root) else os.path.dirname(resolved_impl_dir)

        # Add temporary sys path for imports outside the project root
        temporary_sys_path = None
        if base_dir != project_root:
            logger.debug('Found different base directory compared to the project root: {}'.format(base_dir, f"{resolved_impl_dir}"))
            temporary_sys_path = base_dir

        _import_impl(base_dir, resolved_impl_dir, temporary_sys_path)


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


def _import_impl(base_dir: str, absolute_step_impl_dir: str, temporary_sys_path: Optional[str]):
    for python_file in glob.glob(f"{absolute_step_impl_dir}/**/*.py", recursive=True):
        if python_file.endswith("__init__.py"):
            continue
        relative_path = os.path.normpath(python_file.replace(base_dir + os.path.sep, ''))
        module_name = os.path.splitext(relative_path.replace(os.path.sep, '.'))[0]
        _import_file(module_name, python_file, temporary_sys_path)

@contextmanager
def use_temporary_sys_path(temporary_sys_path: str):
    original_sys_path = sys.path[:]
    sys.path.append(temporary_sys_path)
    try:
        yield
    finally:
        sys.path = original_sys_path

def _import_file(module_name: str, file_path: str, temporary_sys_path: Optional[str]):
    try:
        logger.debug('Import module {} with path {}'.format(module_name, file_path))

        # Use temporary sys path for relative imports
        if temporary_sys_path is not None:
            logger.debug('Import module {} using temporary sys path {}'.format(module_name, temporary_sys_path))
            with use_temporary_sys_path(temporary_sys_path):
                m = importlib.import_module(module_name)
        else:
            m = importlib.import_module(module_name)

        # Get all classes in the imported module
        classes = inspect.getmembers(m, lambda member: inspect.isclass(member) and member.__module__ == module_name)
        if len(classes) > 0:
            for c in classes:
                class_obj = c[1]
                if _has_methods_with_gauge_decoratores(class_obj):
                    update_step_registry_with_class(
                        instance=class_obj(), # class_obj() will create a new instance of the class
                        file_path=file_path
                    )
    except:
        logger.fatal('Exception occurred while loading step implementations from file: {}.\n{}'.format(file_path, traceback.format_exc()))

def update_step_registry_with_class(instance, file_path: str):
    """ Inject instance in each class method (hook/step) """
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
