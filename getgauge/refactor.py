import re

from redbaron import RedBaron, ast

from getgauge.registry import registry


def refactor_step(request, response):
    if registry.has_multiple_impls(request.refactorRequest.oldStepValue.stepValue):
        step = request.refactorRequest.oldStepValue.parameterizedStepValue
        raise Exception('Multiple Implementation found for `{}`'.format(step))
    info = registry.get_info_for(request.refactorRequest.oldStepValue.stepValue)
    impl_file = open(info.file_name, 'r+')
    content = _refactor_content(impl_file.read(), info, request)
    if request.refactorRequest.saveChanges:
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
    decorator.call = '("' + request.refactorRequest.newStepValue.parameterizedStepValue + '")'
    params = [''] * len(request.refactorRequest.newStepValue.parameters)
    for index, position in enumerate(request.refactorRequest.paramPositions):
        if position.oldPosition < 0:
            param = request.refactorRequest.newStepValue.parameters[index]
            params[position.newPosition] = _get_param_name("arg{}".format(position.newPosition), param)
        else:
            params[position.newPosition] = func.arguments[position.oldPosition].__str__()
    func.arguments = ', '.join(params)


def _get_param_name(prefix, param_name):
    return param_name if _is_valid(param_name) else prefix


def _is_valid(name):
    try:
        ast.parse("{} = None".format(name))
        return True
    except:
        return False
