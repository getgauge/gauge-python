import logging
import re
from os import path

from redbaron import RedBaron

from getgauge.registry import registry
from getgauge.util import *


def load_steps(ast, file_name):
    if ast is not None:
        for func in ast.find_all('def'):
            for decorator in func.decorators:
                if decorator.value.__str__() == 'step':
                    steps = re.findall(
                        r'[\'"](.*?)[\'"]', decorator.call.__str__())
                    add_steps(file_name, func, steps)


def generate_ast(content, file_name):
    try:
        return RedBaron(content)
    except Exception:
        logging.error("Failed to parse {}.".format(file_name))
        return


def reload_steps(content, file_name):
    ast = generate_ast(content, file_name)
    if ast is not None:
        registry.remove_steps(file_name)
        load_steps(ast, file_name)


def _create_span(func):
    try:
        start = func.absolute_bounding_box.top_left
        end = func.absolute_bounding_box.bottom_right
        return {"start": start.line, "startChar": start.column, "end": end.line, "endChar": end.column}
    except:
        return {"start": 0, "startChar": 0, "end": 0, "endChar": 0}


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
            ast = generate_ast(impl_file.read(), file_path)
            if ast is not None:
                load_steps(ast, file_path)
            impl_file.close()
        elif path.isdir(file_path):
            load_files(file_path)
