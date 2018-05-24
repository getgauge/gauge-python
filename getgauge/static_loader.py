import logging
import re
import os

from redbaron import RedBaron

from getgauge.registry import registry


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


def add_steps(file_name, func, steps):
    if len(steps) > 1:
        registry.add_step(steps, func, file_name, None)
    elif len(steps) == 1:
        registry.add_step(steps[0], func, file_name, None)


def load_files(step_impl_dir):
    for f in os.listdir(step_impl_dir):
        file_path = os.path.join(step_impl_dir, f)
        if f.endswith('.py'):
            impl_file = open(file_path, 'r+')
            ast = generate_ast(impl_file.read(), file_path)
            if ast is not None:
                load_steps(ast, file_path)
            impl_file.close()
        elif os.path.isdir(file_path):
            load_files(file_path)
