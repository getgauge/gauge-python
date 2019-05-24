import os

PROJECT_ROOT_ENV = 'GAUGE_PROJECT_ROOT'
STEP_IMPL_DIR_ENV = 'STEP_IMPL_DIR'


def get_project_root():
    try:
        return os.path.abspath(os.environ[PROJECT_ROOT_ENV])
    except KeyError:
        return ""


def get_step_impl_dirs():
    step_impl_dir_names = map(str.strip, os.getenv(STEP_IMPL_DIR_ENV).split(',')) if os.getenv(STEP_IMPL_DIR_ENV) else ['step_impl']
    full_path_dir_names = []
    for name in step_impl_dir_names:
        name = name.replace("/", os.path.sep).replace("\\", os.path.sep)
        imple_dir = name if os.path.isabs(name) else os.path.join(get_project_root(), name)
        full_path_dir_names.append(imple_dir)
    return full_path_dir_names


def get_impl_files():
    step_impl_dirs = get_step_impl_dirs()
    file_list = []
    for step_impl_dir in step_impl_dirs:
        for root, _, files in os.walk(step_impl_dir):
            for file in files:
                if file.endswith('.py') and '__init__.py' != os.path.basename(file):
                    file_list.append(os.path.join(root, file))
    return file_list


def read_file_contents(file_name):
    if os.path.isfile(file_name):
        f = open(file_name)
        content = f.read().replace('\r\n', '\n')
        f.close()
        return content
    return None


def get_file_name(prefix='', counter=0):
    name = 'step_implementation{}.py'.format(prefix)
    file_name = os.path.join(get_step_impl_dirs()[0], name)
    if not os.path.exists(file_name):
        return file_name
    else:
        counter = counter + 1
        return get_file_name('_{}'.format(counter), counter)
