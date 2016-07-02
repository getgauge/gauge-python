import re

from redbaron import RedBaron

from getgauge.registry import registry


def _refactor_content(content, info, request):
    red = RedBaron(content)
    for func in red.find_all('def'):
        for decorator in func.decorators:
            steps = re.findall(r'[\'"](.*?)[\'"]', decorator.call.__str__())
            if len(steps) > 0 and steps[0] == info.step_text:
                refactor_impl(decorator, func, request)
    return red.dumps()


def refactor_impl(decorator, func, request):
    decorator.call = '("' + request.refactorRequest.newStepValue.parameterizedStepValue + '")'
    params = [''] * len(request.refactorRequest.newStepValue.parameters)
    for index, position in enumerate(request.refactorRequest.paramPositions):
        if position.oldPosition < 0:
            params[position.newPosition] = request.refactorRequest.newStepValue.parameters[index]
        else:
            params[position.newPosition] = func.arguments[position.oldPosition].__str__()
    func.arguments = ', '.join(params)


def refactor_step(request, response):
    if registry.has_multiple_impls(request.refactorRequest.oldStepValue.stepValue):
        raise Exception('Multiple Implementation found for `{}`'.format(request.refactorRequest.oldStepValue.parameterizedStepValue))
    info = registry.get_info(request.refactorRequest.oldStepValue.stepValue)
    impl_file = open(info.file_name, 'r+')
    content = _refactor_content(impl_file.read(), info, request)
    impl_file.seek(0)
    impl_file.truncate()
    impl_file.write(content)
    impl_file.close()
    response.refactorResponse.success = True
    response.refactorResponse.filesChanged.append(info.file_name)
