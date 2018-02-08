import re
from os import path

from baron.utils import BaronError
from redbaron import RedBaron

from getgauge.registry import registry
from getgauge.util import *


def load_steps(content, file_name):
    try:
        red = RedBaron(content)
        for func in red.find_all('def'):
            for decorator in func.decorators:
                if decorator.value.__str__() == 'step':
                    steps = re.findall(r'[\'"](.*?)[\'"]', decorator.call.__str__())
                    add_steps(file_name, func, steps)
    except BaronError as e:
        print(e.args[0][:-640])



def reload_steps(content, file_name):
    registry.remove_steps(file_name)
    load_steps(content, file_name)


def _create_span(func):
    start = func.absolute_bounding_box.top_left
    end = func.absolute_bounding_box.bottom_right
    return {"start": start.line, "startChar": start.column, "end": end.line, "endChar": end.column}


def add_steps(file_name, func, steps):
    if len(steps) > 1:
        registry.add_step(steps, func, file_name, _create_span(func))
    elif len(steps) == 1:
        registry.add_step(steps[0], func, file_name, _create_span(func))


def load_files(step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            impl_file = open(file_path, 'r+')
            load_steps(impl_file.read(), file_path)
            impl_file.close()
        elif path.isdir(file_path):
            load_files(file_path)
