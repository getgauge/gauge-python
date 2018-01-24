import os

PROJECT_ROOT_ENV = 'GAUGE_PROJECT_ROOT'
STEP_IMPL_DIR_ENV = 'STEP_IMPL_DIR'
STEP_IMPL_DIR_NAME = os.getenv(STEP_IMPL_DIR_ENV) or 'step_impl'


def get_project_root():
    try:
        return os.path.abspath(os.environ[PROJECT_ROOT_ENV])
    except KeyError:
        return ""


def get_step_impl_dir():
    return os.path.join(get_project_root(), STEP_IMPL_DIR_NAME)
