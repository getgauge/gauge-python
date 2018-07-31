import six
import logging
from redbaron import RedBaron


class RedbaronPythonFile(object):
    @staticmethod
    def parse(file_path, content=None):
        '''
        Create a PythonFile object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        try:
            if content is None:
                with open(file_path) as f:
                    content = f.read()
            py_tree = RedBaron(content)
            return RedbaronPythonFile(file_path, py_tree)
        except Exception as ex:
            # Trim parsing error message to only include failure location
            msg = str(ex)
            marker = "<---- here\n"
            marker_pos = msg.find(marker)
            if marker_pos > 0:
                msg = msg[:marker_pos+len(marker)]
            logging.error("Failed to parse {}: {}".format(file_path, msg))

    def __init__(self, file_path, py_tree):
        # type: (str, RedBaron)
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
        # type: () -> Generator[redbaron.nodes.DefNode, redbaron.nodes.DecoratorNode]
        '''Find top level functions with step decorator in parsed file'''
        for node in self.py_tree:
            if node.type == 'def':
                for decorator in node.decorators:
                    if decorator.name.value == 'step':
                        yield node, decorator
                        break

    def _step_decorator_args(self, decorator):
        # type: (redbaron.nodes.DecoratorNode) -> Optional(Union[str, List[str]])
        '''Get the arguments passed to step decorators converted to python objects'''
        args = decorator.call.value
        step = None
        if len(args) == 1:
            try:
                step = args[0].value.to_python()
            except (ValueError, SyntaxError):
                pass
            if isinstance(step, six.string_types+(list,)):
                return step
            logging.error("Decorator step accepts either a string or a list of strings - %s",
                          self.file_path)
        else:
            logging.error("Decorator step accepts only one argument - %s",
                          self.file_path)

    def iter_steps(self):
        # type: () -> Generator[FunctionSteps]
        '''Iterate over steps in the parsed file'''
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            if step:
                yield step, func.name, self._span_for_node(func, True)

    def _find_step_node(self, step_text):
        # type: (str) -> Optional[Tuple[redbaron.nodes.StringNode, redbaron.nodes.DefNode]]
        '''Find the ast node which contains the text'''
        for func, decorator in self._iter_step_func_decorators():
            step = self._step_decorator_args(decorator)
            arg_node = decorator.call.value[0].value
            if step == step_text:
                return arg_node, func
            elif isinstance(step, list) and step_text in step:
                step_node = arg_node[step.index(step_text)]
                return step_node, func
        return None, None

    def refactor_step(self, old_text, new_text, move_param_from_idx):
        # type: (str, str, List[int]) -> List[Tuple[Span, str]]
        '''
        Find the step with old_text and change it to new_text. The step function
        parameters are also changed accoring to move_param_from_idx. Each entry in
        this list should specify parameter position from old
        '''
        step, func = self._find_step_node(old_text)
        if step is None:
            return []
        step_span = self._span_for_node(step, False)
        step.value = step.value.replace(old_text, new_text)
        diffs = [(step_span, step.value)]
        old_params = func.arguments
        # Check if any parameters have moved
        if len(old_params) == len(move_param_from_idx) and all(i == v for (i, v) in enumerate(move_param_from_idx)):
            return diffs
        params_span = self._span_for_node(old_params, False)
        new_params = []
        for i, move_from in enumerate(move_param_from_idx):
            if move_from < 0:
                name = 'arg{}'.format(i)
            else:
                name = old_params[move_from].name.value
            new_params.append(name)
        func.arguments = ', '.join(new_params)
        diffs.append((params_span, func.arguments.dumps()))
        return diffs

    def get_code(self):
        # type: () -> str
        '''Returns current content of the tree.'''
        return self.py_tree.dumps()
