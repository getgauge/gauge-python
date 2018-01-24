import re

from os import path
from redbaron import RedBaron
from baron.utils import BaronError

from getgauge.util import *
from getgauge.registry import registry


def load_file(content, file_name):
    try:
        red = RedBaron(content)
        for func in red.find_all('def'):
            for decorator in func.decorators:
                if decorator.value.__str__() == 'step':
                    steps = re.findall(r'[\'"](.*?)[\'"]', decorator.call.__str__())
                    add_steps(file_name, func, steps)
    except BaronError:
        pass


def add_steps(file_name, func, steps):
    if len(steps) > 1:
        registry.add_step(steps, func, file_name, func.absolute_bounding_box.top_left.line)
    elif len(steps) == 1:
        registry.add_step(steps[0], func, file_name, func.absolute_bounding_box.top_left.line)


def load_files(step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            impl_file = open(file_path, 'r+')
            load_file(impl_file.read(), file_path)
            impl_file.close()
        elif path.isdir(file_path):
            load_files(file_path)
