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

def list_impl_files(file_list,step_impl_dir = get_step_impl_dir()):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            file_list.append(os.path.join(step_impl_dir, f))
        elif os.path.isdir(file_path):
            list_impl_files(file_list,file_path)

def read_file_contents(fileName):
    if os.path.isfile(fileName):
        f = open(fileName)
        content = f.read()
        f.close()
        return content
    return ""