import inspect
import os
import sys
import time
import traceback

from getgauge.messages.messages_pb2 import Message
from getgauge.messages.spec_pb2 import ProtoExecutionResult
from getgauge.registry import registry


def set_response_values(request, response):
    response.messageType = Message.ExecutionStatusResponse
    response.executionStatusResponse.executionResult.failed = False
    response.executionStatusResponse.executionResult.executionTime = 0


def run_hook(request, response, hooks, execution_info):
    set_response_values(request, response)
    for hook in hooks:
        args = _get_args(execution_info, hook)
        execute_method(args, hook, response)


def _false(func, exception): return False


def execute_method(params, func, response, is_continue_on_failure=_false):
    start = _current_time()
    try:
        func(*params)
    except Exception as e:
        _add_exception(e, response, is_continue_on_failure(func, e))
    response.executionStatusResponse.executionResult.executionTime = _current_time() - start


def _current_time(): return int(round(time.time() * 1000))


def _get_args(execution_info, hook):
    if sys.version_info < (3, 3):
        return [] if len(inspect.getargspec(hook).args) == 0 else [execution_info]
    else:
        return [] if len(inspect.signature(hook).parameters) == 0 else [execution_info]


def _add_exception(e, response, continue_on_failure):
    if os.getenv('screenshot_on_failure') == 'true':
        response.executionStatusResponse.executionResult.screenShot = registry.screenshot_provider()()
    response.executionStatusResponse.executionResult.failed = True
    message = e.__str__()
    if not message:
        message = "Exception occurred"
    response.executionStatusResponse.executionResult.errorMessage = message
    response.executionStatusResponse.executionResult.stackTrace = traceback.format_exc()
    response.executionStatusResponse.executionResult.errorType = ProtoExecutionResult.ASSERTION
    if continue_on_failure:
        response.executionStatusResponse.executionResult.recoverableError = True
