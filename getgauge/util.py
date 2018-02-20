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


def list_impl_files():
    step_impl_dir = get_step_impl_dir()
    file_list = []
    for root, _, files in os.walk(step_impl_dir):
        for file in files:
            if file.endswith('.py'):
                file_list.append(os.path.join(root, file))
    return file_list


def read_file_contents(file_name):
    if os.path.isfile(file_name):
        f = open(file_name)
        content = f.read()
        f.close()
        return content
    return ""
