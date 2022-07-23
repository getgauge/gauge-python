from getgauge import logger
from redbaron import RedBaron


class Parser(object):

    @staticmethod
    def parse(file_path, content=None):
        """
        Create a Parser object with specified file_path and content.
        If content is None then, it is loaded from the file_path method.
        Otherwise, file_path is only used for reporting errors.
        """
        try:
            if content is None:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
            py_tree = RedBaron(content)
            return Parser(file_path, py_tree)
        except Exception as ex:
            # Trim parsing error message to only include failure location
            msg = str(ex)
            marker = "<---- here\n"
            marker_pos = msg.find(marker)
            if marker_pos > 0:
                msg = msg[:marker_pos + len(marker)]
            logger.error("Failed to parse {}: {}".format(file_path, msg))

    def __init__(self, file_path, py_tree):
        self.file_path = file_path
        self.py_tree = py_tree

    def _span_for_node(self, node, lazy=False):
        def calculate_span():
            try:
                # For some reason RedBaron does not create absolute_bounding_box
                # attributes for some content passed during unit test so we have
                # to catch AttributeError here and return invalid data
                box = node.absolute_bounding_box
                # Column numbers start at 1 where-as we want to start at 0. Also
                # column 0 is used to indicate end before start of line.
                return {
                    'start': box.top_left.line,
                    'startChar': max(0, box.top_left.column - 1),
                    'end': box.bottom_right.line,
                    'endChar': max(0, box.bottom_right.column),
                }
            except AttributeError:
                return {'start': 0, 'startChar': 0, 'end': 0, 'endChar': 0}

        return calculate_span if lazy else calculate_span()

    def _iter_step_func_decorators(self):
        """Find functions with step decorator in parsed file."""
        for node in self.py_tree.find_all('def'):
            for decorator in node.decorators:
                try:
                    if decorator.name.value == 'step':
                        yield node, decorator
                        break
                except AttributeError:
                    continue

    def _step_decorator_args(self, decorator):
        """
        Get arguments passed to step decorators converted to python objects.
        """
        args = decorator.call.value
        step = None
        if len(args) == 1:
            try:
                step = args[0].value.to_python()
            except (ValueError, SyntaxError):
                pass
            if isinstance(step, str) or isinstance(step, list):
                return step
            logger.error("Decorator step accepts either a string or a list of \
                strings - {0}".format(self.file_path))
        else:
            logger.error("Decorator step accepts only one argument - {0}".format(self.file_path))

    def iter_steps(self):
        """Iterate over steps in the parsed file."""
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            if step:
                yield step, func.name, self._span_for_node(func, True)

    def _find_step_node(self, step_text):
        """Find the ast node which contains the text."""
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            arg_node = decorator.call.value[0].value
            if step == step_text:
                return arg_node, func
            elif isinstance(step, list) and step_text in step:
                step_node = arg_node[step.index(step_text)]
                return step_node, func
        return None, None

    def _refactor_step_text(self, step, old_text, new_text):
        step_span = self._span_for_node(step, False)
        step.value = step.value.replace(old_text, new_text)
        return step_span, step.value

    def _get_param_name(self, param_nodes, i):
        name = 'arg{}'.format(i)
        if name not in [x.name.value for x in param_nodes]:
            return name
        return self._get_param_name(param_nodes, i + 1)

    def _move_params(self, params, move_param_from_idx):
        # If the move list is exactly same as current params
        # list then no need to create a new list.
        if list(range(len(params))) == move_param_from_idx:
            return params
        new_params = []
        for (new_idx, old_idx) in enumerate(move_param_from_idx):
            if old_idx < 0:
                new_params.append(self._get_param_name(params, new_idx))
            else:
                new_params.append(params[old_idx].name.value)
        return ', '.join(new_params)

    def refactor_step(self, old_text, new_text, move_param_from_idx):
        """
        Find the step with old_text and change it to new_text.
        The step function parameters are also changed according
        to move_param_from_idx.  Each entry in this list should
        specify parameter position from old
        """
        diffs = []
        step, func = self._find_step_node(old_text)
        if step is None:
            return diffs
        step_diff = self._refactor_step_text(step, old_text, new_text)
        diffs.append(step_diff)
        moved_params = self._move_params(func.arguments, move_param_from_idx)
        if func.arguments is not moved_params:
            params_span = self._span_for_node(func.arguments, False)
            func.arguments = moved_params
            diffs.append((params_span, func.arguments.dumps()))
        return diffs

    def get_code(self):
        """Return current content of the tree."""
        return self.py_tree.dumps()
