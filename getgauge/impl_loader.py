import os
import py_compile
import shutil
import sys
from os import path

PROJECT_ROOT_ENV = 'GAUGE_PROJECT_ROOT'
STEP_IMPL_DIR = "step_impl"

project_root = os.environ[PROJECT_ROOT_ENV]
impl_dir = os.path.join(project_root, STEP_IMPL_DIR)
sys.path.append(impl_dir)


def load_impls():
    modules = []
    _load_impls_in(modules, impl_dir)
    map(__import__, modules)


def _load_impls_in(modules, step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith(".py"):
            py_compile.compile(file_path)
            modules.append(os.path.splitext(f)[0])
        elif path.isdir(step_impl_dir + f):
            sys.path.append(step_impl_dir + f)
            _load_impls_in(modules, file_path)


def copy_impl():
    try:
        print("Initialising Gauge Python project")
        print("create  {}".format(impl_dir))
        shutil.copytree(STEP_IMPL_DIR, impl_dir)
    except Exception as e:
        print('Skipped copying implementation: {}.'.format(e))
