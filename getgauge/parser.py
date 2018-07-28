import ast
import parso
import logging


def _span_for_node(node):
    return {
        'start': node.start_pos[0], 'startChar': node.start_pos[1],
        'end': node.end_pos[0], 'endChar': node.end_pos[1],
    }


class PythonFile(object):
    def __init__(self, file_path, content=None):
        self.content = content
        self.file_path = file_path

    def parse(self):
        try:
            self.ast = parso.parse(self.content, path=self.file_name, error_recovery=False)
            return True
        except parso.parser.ParserSyntaxError as ex:
            logging.error("Failed to parse %s:%d '%s'", self.file_name, ex.error_leaf.line, ex.error_leaf.get_code())
            self.ast = None
        return False

    def _iter_step_func_decorators(self):
        for func in self.ast.iter_funcdefs():
            for decorator in func.get_decorators():
                if decorator.children[1].value == 'step':
                    yield func, decorator
                    break

    def _step_decorator_args(self, decorator):
        args = decorator.children[3:-2]
        if len(args) == 1:
            try:
                return ast.literal_eval(args[0].get_code())
            except ValueError:
                logging.error("Decorator step accepts either a string or a list of strings - %s:%d",
                              self.file_path, decorator.start_pos[0])
            except SyntaxError:
                pass
        else:
            logging.error("Decorator step accepts only one argument - %s:%d",
                          self.file_path, decorator.start_pos[0])

    def iter_steps(self):
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            if step:
                yield step, func, self.file_path, _span_for_node(func)

    def find_step_node(self, step_text):
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            arg_node = decorator.children[3]
            if step == step_text:
                return arg_node, decorator, func
            elif isinstance(step, list) and step_text in step:
                idx = step.index(step_text)
                step_node = arg_node.children[1].children[idx * 2]
                return step_node, func
        return None, None

    def refactor_step(self, old_text, new_text, new_param_positions):
        step, func = self.find_step_node(old_text)
        if step is None:
            return
        step_span = _span_for_node(step)
        step.value = step.value.replace(old_text, new_text)
        diffs = [(step_span, step.value)]
        params_span = _span_for_node(func.children[2])
        params = func.get_params()
        param_names = [p.name.value for p in params]
        func_changed = False
        for cur_pos, param in enumerate(params):
            new_pos = new_param_positions[cur_pos]
            if new_pos != cur_pos:
                param.name.value = param_names[new_pos]
                func_changed = True
        if func_changed:
            diffs.append(params_span, func.get_code(include_prefix=False))
        return diffs

    def get_code(self):
        if self.ast:
            return self.ast.get_code()

    def save(self, new_path=None):
        file_path = new_path or self.file_path
        with open(file_path, 'w') as f:
            f.write(self.get_code())
