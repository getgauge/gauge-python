import logging
import os

from redbaron import RedBaron

from getgauge.registry import registry


def span_for_node(node):
    try:
        # For some reason RedBaron does not create absolute_bounding_box
        # attributes for some content passed during unit test so we have
        # to catch AttributeError here and return invalid data
        box = node.absolute_bounding_box
        return {
            'start': box.top_left.line,
            'startChar': box.top_left.column,
            'end': box.bottom_right.line,
            'endChar': box.bottom_right.column,
        }
    except AttributeError:
        return {'start': 0, 'startChar': 0, 'end': 0, 'endChar': 0}


def load_steps(ast, file_name):
    for func in ast.find_all('def'):
        # Check if function has a step decorator
        decorator = next((d for d in func.decorators if d.name.value == 'step'), None)
        if not decorator:
            continue
        # The step decorator should have at least one argument
        args = decorator.call.value
        if len(args) < 1:
            continue
        step_arg = args[0].value
        if step_arg.type == 'list':
            # If a list is provided as the first argument,
            # it must have all values as strings
            if any(v.type != 'string' for v in step_arg.value):
                continue
        elif step_arg.type != 'string':
            # Otherwise the argument must be a string
            continue
        steps = step_arg.to_python()
        span = span_for_node(func)
        registry.add_step(steps, func, file_name, span)


def generate_ast(content, file_name):
    try:
        return RedBaron(content)
    except Exception as ex:
        # Trim parsing error message to only include failure location
        msg = str(ex)
        marker = "<---- here\n"
        marker_pos = msg.find(marker)
        if marker_pos > 0:
            msg = msg[:marker_pos+len(marker)]
        logging.error("Failed to parse {}: {}".format(file_name, msg))
        return


def reload_steps(content, file_name):
    ast = generate_ast(content, file_name)
    if ast is not None:
        registry.remove_steps(file_name)
        load_steps(ast, file_name)


def add_steps(file_name, func, steps):
    if isinstance(steps, list) or isinstance(steps, str):
        registry.add_step(steps, func, file_name, None)


def load_files(step_impl_dir):
    for dirpath, dirs, files in os.walk(step_impl_dir):
        py_files = (os.path.join(dirpath, f) for f in files if f.endswith('.py'))
        for file_path in py_files:
            with open(file_path, 'r') as impl_file:
                ast = generate_ast(impl_file.read(), file_path)
                if ast is not None:
                    load_steps(ast, file_path)
