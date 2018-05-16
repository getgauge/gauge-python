import copy
import re

from redbaron import RedBaron, ast

from getgauge.messages.messages_pb2 import TextDiff
from getgauge.registry import registry


def refactor_step(request, response, with_location=True):
    if registry.has_multiple_impls(request.oldStepValue.stepValue):
        step = request.oldStepValue.parameterizedStepValue
        raise Exception('Multiple Implementation found for `{}`'.format(step))
    info = registry.get_info_for(request.oldStepValue.stepValue)
    impl_file = open(info.file_name, 'r+')
    content, diff = _refactor_content(impl_file.read(), info, request, with_location)
    if request.saveChanges:
        impl_file.seek(0)
        impl_file.truncate()
        impl_file.write(content)
    impl_file.close()
    response.refactorResponse.success = True
    response.refactorResponse.filesChanged.append(info.file_name)
    response.refactorResponse.fileChanges.add(**{'fileName': info.file_name, 'fileContent': content, 'diffs': diff})


def _refactor_content(content, info, request, with_location):
    red = RedBaron(content)
    diff = None
    for func in red.find_all('def'):
        for decorator in func.decorators:
            steps = re.findall(r'[\'"](.*?)[\'"]', decorator.call.__str__())
            if len(steps) > 0 and steps[0] == info.step_text:
                diff = _refactor_impl(decorator, func, request, with_location)
    return red.dumps(), diff


def create_diff(old_call_loc, step, old_params_loc, params, with_location):
    annotation_diff, func_diff = TextDiff(), TextDiff()
    annotation_diff.content = step
    func_diff.content = params
    if with_location:
        annotation_diff.span.start = old_call_loc.top_left.line
        annotation_diff.span.startChar = old_call_loc.top_left.column - 1
        annotation_diff.span.end = old_call_loc.bottom_right.line
        annotation_diff.span.endChar = old_call_loc.bottom_right.column
        func_diff.span.start = old_params_loc.top_left.line
        func_diff.span.startChar = old_params_loc.top_left.column - 1
        func_diff.span.end = old_params_loc.bottom_right.line
        func_diff.span.endChar = old_params_loc.bottom_right.column
    return [annotation_diff, func_diff]


def _refactor_impl(decorator, func, request, with_location):
    old_call_loc, old_params_loc = None, None
    if with_location:
        old_call_loc = copy.deepcopy(decorator.call.absolute_bounding_box)
        old_params_loc = copy.deepcopy(func.arguments.node_list.absolute_bounding_box)
    decorator.call = '("' + request.newStepValue.parameterizedStepValue + '")'
    params = [''] * len(request.newStepValue.parameters)
    for index, position in enumerate(request.paramPositions):
        if position.oldPosition < 0:
            param = request.newStepValue.parameters[index]
            params[position.newPosition] = _get_param_name("arg{}".format(position.newPosition), param)
        else:
            params[position.newPosition] = func.arguments[position.oldPosition].__str__()
    func.arguments = ', '.join(params)
    return create_diff(old_call_loc, str(decorator.call), old_params_loc, ', '.join(params), with_location)


def _get_param_name(prefix, param_name):
    return param_name if _is_valid(param_name) else prefix


def _is_valid(name):
    try:
        ast.parse("{} = None".format(name))
        return True
    except:
        return False
