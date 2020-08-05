import ast

import parso
import six
from getgauge import logger

# Reuse parser for multiple invocations. This also prevents
# problems with pyfakefs during testing for Python 3.7
_parser = parso.load_grammar()


class ParsoPythonFile(object):

    @staticmethod
    def parse(file_path, content=None):
        """
        Create a PythonFile object with specified file_path and content.
        If content is None then, it is loaded from the file_path method.
        Otherwise, file_path is only used for reporting errors.
        """
        try:
            # Parso reads files in binary mode and converts to unicode
            # using python_bytes_to_unicode() function. As a result,
            # we no longer have information about original file encoding and
            # output of module.get_content() can't be converted back to bytes
            # For now we can make a compromise by reading the file ourselves
            # and passing content to parse() function.
            if content is None:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
            py_tree = _parser.parse(
                content, path=file_path, error_recovery=False)
            return ParsoPythonFile(file_path, py_tree)
        except parso.parser.ParserSyntaxError as ex:
            logger.error("Failed to parse {0}:{1} '{2}'".format(file_path, ex.error_leaf.line, ex.error_leaf.get_code()))

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
        """Find functions with step decorator in parsed file"""
        func_defs = [func for func in self.py_tree.iter_funcdefs()] + [func for cls in self.py_tree.iter_classdefs() for func in cls.iter_funcdefs()]
        for func in func_defs:
            for decorator in func.get_decorators():
                try:
                    if decorator.children[1].value == 'step':
                        yield func, decorator
                        break
                except AttributeError:
                        continue

    def _step_decorator_args(self, decorator):
        """
        Get the arguments passed to step decorators
        converted to python objects.
        """
        args = decorator.children[3:-2]
        step = None
        if len(args) == 1:
            try:
                step = ast.literal_eval(args[0].get_code())
            except (ValueError, SyntaxError):
                pass
            if isinstance(step, six.string_types+(list,)):
                return step
            logger.error("Decorator step accepts either a string or a list of strings - {1}:{0}".format(self.file_path, decorator.start_pos[0]))
        else:
            logger.error("Decorator step accepts only one argument - {0}:{1}".format(self.file_path, decorator.start_pos[0]))

    def iter_steps(self):
        """Iterate over steps in the parsed file."""
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            if step:
                span = self._span_from_pos(decorator.start_pos, func.end_pos)
                yield step, func.name.value, span

    def _find_step_node(self, step_text):
        """Find the ast node which contains the text."""
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

    def _refactor_step_text(self, step, old_text, new_text):
        step_span = self._span_from_pos(step.start_pos, step.end_pos)
        step.value = step.value.replace(old_text, new_text)
        return step_span, step.value

    def _create_param_node(self, parent, name, prefix, is_last):
        start_pos = parent[-1].end_pos[0], parent[-1].end_pos[1] + len(prefix)
        children = [parso.python.tree.Name(name, start_pos, prefix)]
        if not is_last:
            children.append(parso.python.tree.Operator(
                ',', children[-1].end_pos))
        return parso.python.tree.Param(children, parent)

    def _move_param_nodes(self, param_nodes, move_param_from_idx):
        # Param nodes include opening and closing braces
        num_params = len(param_nodes) - 2
        # If the move list is exactly same as current params
        # list then no need to create a new list.
        if list(range(num_params)) == move_param_from_idx:
            return param_nodes
        # Get the prefix from second parameter to use with new parameters
        prefix = param_nodes[2].name.prefix if num_params > 1 else ' '
        new_param_nodes = [parso.python.tree.Operator(
            '(', param_nodes[0].start_pos)]
        for i, move_from in enumerate(move_param_from_idx):
            param = self._create_param_node(
                new_param_nodes,
                self._get_param_name(
                    param_nodes, i) if move_from < 0 else param_nodes[move_from + 1].name.value,
                '' if i == 0 else prefix,
                i >= len(move_param_from_idx) - 1
            )
            new_param_nodes.append(param)
        new_param_nodes.append(parso.python.tree.Operator(
            ')', new_param_nodes[-1].end_pos))
        # Change the parent to actual function
        for node in new_param_nodes:
            node.parent = param_nodes[0].parent
        return new_param_nodes

    def refactor_step(self, old_text, new_text, move_param_from_idx):
        """
        Find the step with old_text and change it to new_text.The step function
        parameters are also changed according to move_param_from_idx.
        Each entry in this list should specify parameter position from old.
        """
        diffs = []
        step, func = self._find_step_node(old_text)
        if step is None:
            return diffs
        step_diff = self._refactor_step_text(step, old_text, new_text)
        diffs.append(step_diff)
        params_list_node = func.children[2]
        moved_params = self._move_param_nodes(
            params_list_node.children, move_param_from_idx)
        if params_list_node.children is not moved_params:
            # Record original parameter list span excluding braces
            params_span = self._span_from_pos(
                params_list_node.children[0].end_pos,
                params_list_node.children[-1].start_pos)
            params_list_node.children = moved_params
            # Get code for moved paramters excluding braces
            param_code = ''.join(p.get_code() for p in moved_params[1:-1])
            diffs.append((params_span, param_code))
        return diffs

    def get_code(self):
        """Return current content of the tree."""
        return self.py_tree.get_code()

    def _get_param_name(self, param_nodes, i):
        name = 'arg{}'.format(i)
        if name not in [x.name.value for x in param_nodes[1:-1]]:
            return name
        else:
            return self._get_param_name(param_nodes, i + 1)
