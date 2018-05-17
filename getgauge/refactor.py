import re

from redbaron import RedBaron, ast

from getgauge.registry import registry


def refactor_step(request, response):
    if registry.has_multiple_impls(request.oldStepValue.stepValue):
        step = request.oldStepValue.parameterizedStepValue
        raise Exception('Multiple Implementation found for `{}`'.format(step))
    info = registry.get_info_for(request.oldStepValue.stepValue)
    impl_file = open(info.file_name, 'r+')
    content = _refactor_content(impl_file.read(), info, request)
    if request.saveChanges:
        impl_file.seek(0)
        impl_file.truncate()
        impl_file.write(content)
    impl_file.close()
    response.refactorResponse.fileChanges.add(**{'fileName': info.file_name, 'fileContent': content})
    response.refactorResponse.success = True
    response.refactorResponse.filesChanged.append(info.file_name)


def _refactor_content(content, info, request):
    red = RedBaron(content)
    for func in red.find_all('def'):
        for decorator in func.decorators:
            steps = re.findall(r'[\'"](.*?)[\'"]', decorator.call.__str__())
            if len(steps) > 0 and steps[0] == info.step_text:
                _refactor_impl(decorator, func, request)
    return red.dumps()


def _refactor_impl(decorator, func, request):
    decorator.call = '("' + request.newStepValue.parameterizedStepValue + '")'
    params = [''] * len(request.newStepValue.parameters)
    for index, position in enumerate(request.paramPositions):
        if position.oldPosition < 0:
            params[position.newPosition] = _get_param_name(index, params)
        else:
            params[position.newPosition] = func.arguments[position.oldPosition].__str__()
    func.arguments = ', '.join(params)


def _get_param_name(index, params):
    param = "arg{}".format(index)
    if param not in params:
        return param
    return _get_param_name(index + 1, params)
