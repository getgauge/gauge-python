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


def create_diff(old_annotation_loc, step, old_params_loc, params, with_location):
    annotation_diff, params_diff = TextDiff(), TextDiff()
    annotation_diff.content = step
    params_diff.content = params
    if with_location:
        update_annotation_diff(annotation_diff, old_annotation_loc)
        update_params_diff(params_diff, old_params_loc)
    return [annotation_diff, params_diff]


def update_params_diff(func_diff, old_params_loc):
    func_diff.span.start = old_params_loc.top_left.line  # the line from where first param starts
    func_diff.span.startChar = old_params_loc.top_left.column - 1  # the char position from where the params starts
    func_diff.span.end = old_params_loc.bottom_right.line  # the line no where last param ends
    func_diff.span.endChar = old_params_loc.bottom_right.column  # the char position where the last param ends


def update_annotation_diff(annotation_diff, old_call_loc):
    annotation_diff.span.start = old_call_loc.top_left.line  # the line from where annotation starts
    annotation_diff.span.startChar = old_call_loc.top_left.column - 1  # the char position from where the annotation starts
    annotation_diff.span.end = old_call_loc.bottom_right.line  # the line no where annotation ends
    annotation_diff.span.endChar = old_call_loc.bottom_right.column  # the char position where the annotation starts


def _refactor_impl(decorator, func, request, with_location):
    old_call_loc, old_params_loc = None, None
    if with_location:
        old_call_loc = copy.deepcopy(decorator.call.absolute_bounding_box)
        old_params_loc = copy.deepcopy(func.arguments.node_list.absolute_bounding_box)
    decorator.call = '("' + request.newStepValue.parameterizedStepValue + '")'
    old_params = [arg.target.value for arg in func.arguments][:len(request.oldStepValue.parameters)]
    params = [''] * len(request.newStepValue.parameters)
    for index, position in enumerate(request.paramPositions):
        if position.oldPosition < 0:
            params[position.newPosition] = _get_param_name(index, old_params)
        else:
            params[position.newPosition] = func.arguments[position.oldPosition].__str__()
    func.arguments = ', '.join(params)
    return create_diff(old_call_loc, str(decorator.call), old_params_loc, ', '.join(params), with_location)


def _get_param_name(index, params):
    param = "arg{}".format(index)
    if param not in params:
        return param
    return _get_param_name(index + 1, params)
