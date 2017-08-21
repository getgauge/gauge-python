import inspect
import random
import re
import string
from ast import parse

from colorama import Fore
from colorama import Style

from getgauge.messages.messages_pb2 import Message, StepValidateResponse
from getgauge.registry import registry


def validate_step(request, response):
    response.messageType = Message.StepValidateResponse
    response.stepValidateResponse.isValid = True
    if registry.is_implemented(request.stepValidateRequest.stepText) is False:
        response.stepValidateResponse.errorType = StepValidateResponse.STEP_IMPLEMENTATION_NOT_FOUND
        response.stepValidateResponse.errorMessage = 'Step implementation not found'
        response.stepValidateResponse.isValid = False
        response.stepValidateResponse.suggestion = impl_suggestion(request.stepValidateRequest.stepValue)
    elif registry.has_multiple_impls(request.stepValidateRequest.stepText):
        response.stepValidateResponse.isValid = False
        response.stepValidateResponse.errorType = StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION
        response.stepValidateResponse.suggestion = duplicate_impl_suggestion(request)


def duplicate_impl_suggestion(request):
    return '\n\n' + '\n'.join(
        [(Fore.YELLOW + '{}:{}\n' + Style.RESET_ALL + Style.DIM + '{}' + Style.RESET_ALL).format(
            impl.file_name, impl.line_number, inspect.getsource(impl.impl)) for
         impl in registry.get_infos_for(request.stepValidateRequest.stepText)])


def impl_suggestion(step_value):
    name = re.sub('\s*\{\}\s*', ' ', step_value.stepValue).strip().replace(' ', '_').lower()
    return Fore.YELLOW + """

@step("{}")
def {}({}):
    assert False, "Add implementation code"
""".format(step_value.parameterizedStepValue,
           name if is_valid(name, 'def {}(): return ''') else random_word(),
           format_params(step_value.parameters)) + Style.RESET_ALL


def format_params(params):
    return ', '.join([p if is_valid(p, '{} = None') else 'arg' + str(i + 1) for i, p in enumerate(params)])


def is_valid(name, template):
    try:
        parse(template.format(name))
        return True
    except:
        return False


def random_word(length=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))
