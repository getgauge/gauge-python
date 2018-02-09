import ast
import random
import re
import string

from getgauge.messages.messages_pb2 import Message, StepValidateResponse
from getgauge.registry import registry


def validate_step(request, response):
    response.messageType = Message.StepValidateResponse
    response.stepValidateResponse.isValid = True
    if registry.is_implemented(request.stepValidateRequest.stepText) is False:
        response.stepValidateResponse.errorType = StepValidateResponse.STEP_IMPLEMENTATION_NOT_FOUND
        response.stepValidateResponse.errorMessage = 'Step implementation not found'
        response.stepValidateResponse.isValid = False
        response.stepValidateResponse.suggestion = _impl_suggestion(request.stepValidateRequest.stepValue)
    elif registry.has_multiple_impls(request.stepValidateRequest.stepText):
        response.stepValidateResponse.isValid = False
        response.stepValidateResponse.errorType = StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION
        response.stepValidateResponse.suggestion = _duplicate_impl_suggestion(request)


def _duplicate_impl_suggestion(request):
    text = request.stepValidateRequest.stepText.replace('{}', '<arg>')
    return "Multiple implementations found for `{}`\n".format(text) + '\n'.join(
        ['{}:{}\n''{}'.format(info.file_name, info.span['start'], _format_impl(info.impl.__str__())) for info in
         registry.get_infos_for(request.stepValidateRequest.stepText)])


def _impl_suggestion(step_value):
    name = re.sub('\s*\{\}\s*', ' ', step_value.stepValue).strip().replace(' ', '_').lower()
    return """@step("{}")
def {}({}):
    assert False, "Add implementation code"
""".format(step_value.parameterizedStepValue,
           name if _is_valid(name, 'def {}(): return ''') else _random_word(),
           _format_params(step_value.parameters))


def _format_params(params):
    return ', '.join([p if _is_valid(p) else 'arg' + str(i + 1) for i, p in enumerate(params)])


def _format_impl(impl):
    lines = [l for l in impl.split('\n') if l.strip().startswith('def') or l.strip().startswith('@')]
    return '\n'.join(lines) + '\n   ...\n'


def _is_valid(name, template='{} = None'):
    try:
        ast.parse(template.format(name))
        return True
    except:
        return False


def _random_word(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
