import ast
import six
import parso
import logging


# Reuse parser for multiple invocations. This also prevents
# problems with pyfakefs during testing for Python 3.7
_parser = parso.load_grammar()


class ParsoPythonFile(object):
    @staticmethod
    def parse(file_path, content=None):
        '''
        Create a PythonFile object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        try:
            py_tree = _parser.parse(content, path=file_path, error_recovery=False)
            return ParsoPythonFile(file_path, py_tree)
        except parso.parser.ParserSyntaxError as ex:
            logging.error("Failed to parse %s:%d '%s'", file_path, ex.error_leaf.line, ex.error_leaf.get_code())

    def __init__(self, file_path, py_tree):
        self.file_path = file_path
        self.py_tree = py_tree

    def _span_from_pos(self, start_pos, end_pos):
        return {
            'start': start_pos[0],
            'startChar': start_pos[1],
            'end': end_pos[0],
            'endChar': end_pos[1],
        }

    def _iter_step_func_decorators(self):
        '''Find top level functions with step decorator in parsed file'''
        for func in self.py_tree.iter_funcdefs():
            for decorator in func.get_decorators():
                if decorator.children[1].value == 'step':
                    yield func, decorator
                    break

    def _step_decorator_args(self, decorator):
        '''Get the arguments passed to step decorators converted to python objects'''
        args = decorator.children[3:-2]
        step = None
        if len(args) == 1:
            try:
                step = ast.literal_eval(args[0].get_code())
            except (ValueError, SyntaxError):
                pass
            if isinstance(step, six.string_types+(list,)):
                return step
            logging.error("Decorator step accepts either a string or a list of strings - %s:%d",
                          self.file_path, decorator.start_pos[0])
        else:
            logging.error("Decorator step accepts only one argument - %s:%d",
                          self.file_path, decorator.start_pos[0])

    def iter_steps(self):
        '''Iterate over steps in the parsed file'''
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            if step:
                span = self._span_from_pos(decorator.start_pos, func.end_pos)
                yield step, func.name.value, span

    def _find_step_node(self, step_text):
        '''Find the ast node which contains the text'''
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            arg_node = decorator.children[3]
            if step == step_text:
                return arg_node, func
            elif isinstance(step, list) and step_text in step:
                idx = step.index(step_text)
                step_node = arg_node.children[1].children[idx * 2]
                return step_node, func
        return None, None

    def refactor_step(self, old_text, new_text, move_param_from_idx):
        '''
        Find the step with old_text and change it to new_text. The step function
        parameters are also changed accoring to move_param_from_idx. Each entry in
        this list should specify parameter position from old
        '''
        step, func = self._find_step_node(old_text)
        if step is None:
            return []
        step_span = self._span_from_pos(step.start_pos, step.end_pos)
        step.value = step.value.replace(old_text, new_text)
        diffs = [(step_span, step.value)]
        old_params = func.get_params()
        # Check if any parameters have moved
        if len(old_params) == len(move_param_from_idx) and all(i == v for (i, v) in enumerate(move_param_from_idx)):
            return diffs
        func_params_node = func.children[2]
        params_span = self._span_from_pos(func_params_node.children[0].end_pos, func_params_node.children[-1].start_pos)
        # Use prefix from existing parameter if available
        if len(old_params) > 1:
            param_prefix = old_params[1].name.prefix
        else:
            param_prefix = ' '
        new_params = [parso.python.tree.Operator('(', func_params_node.start_pos)]
        for i, move_from in enumerate(move_param_from_idx):
            # If it is a new parameter name it `arg_x`
            name_prefix = '' if i == 0 else param_prefix
            name = parso.python.tree.Name(
                'arg{}'.format(i) if move_from < 0 else old_params[move_from].name.value,
                (new_params[-1].end_pos[0], new_params[-1].end_pos[1] + len(name_prefix)),
                name_prefix,
            )
            param_nodes = [name]
            # Do not add comma after the last parameter
            if i < len(move_param_from_idx) - 1:
                param_nodes.append(parso.python.tree.Operator(',', param_nodes[-1].end_pos))
            new_param = parso.python.tree.Param(param_nodes, new_params)
            new_params.append(new_param)
        new_params.append(parso.python.tree.Operator(')', new_params[-1].end_pos))
        for p in new_params:
            p.parent = func_params_node
        func_params_node.children = new_params
        # Generate code excluding braces
        param_code = ''.join(p.get_code() for p in new_params[1:-1])
        diffs.append((params_span, param_code))
        return diffs

    def get_code(self):
        '''Returns current content of the tree.'''
        return self.py_tree.get_code()
