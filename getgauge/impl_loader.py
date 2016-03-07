import importlib
import os
import py_compile
import shutil
import sys
import traceback
from os import path

PROJECT_ROOT_ENV = 'GAUGE_PROJECT_ROOT'
STEP_IMPL_DIR = "step_impl"

project_root = os.environ[PROJECT_ROOT_ENV]
impl_dir = os.path.join(project_root, STEP_IMPL_DIR)
sys.path.append(impl_dir)


def load_impls(step_impl_dir=impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith(".py"):
            import_file(f, file_path)
        elif path.isdir(file_path):
            sys.path.append(file_path)
            load_impls(file_path)


def import_file(f, file_path):
    try:
        py_compile.compile(file_path)
        importlib.import_module(os.path.splitext(f)[0])
    except:
        print("Exception occurred while loading step implementations from file: {}.".format(f))
        traceback.print_exc()


def copy_impl():
    try:
        print("Initialising Gauge Python project")
        print("create  {}".format(impl_dir))
        shutil.copytree(STEP_IMPL_DIR, impl_dir)
    except Exception as e:
        print('Skipped copying implementation: {}.'.format(e))
