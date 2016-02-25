import inspect
import os
import tempfile
import time
import traceback
from subprocess import call

from messages.messages_pb2 import Message
from messages.spec_pb2 import ProtoExecutionResult


def _current_time(): return int(round(time.time() * 1000))


def set_response_values(request, response):
    response.messageType = Message.ExecutionStatusResponse
    response.executionStatusResponse.executionResult.failed = False
    response.executionStatusResponse.executionResult.executionTime = 0


def run_hook(request, response, hooks, execution_info):
    set_response_values(request, response)
    for hook in hooks:
        args = [execution_info]
        if len(inspect.getargspec(hook).args) == 0:
            args = []
        execute_method(args, hook, response)


def execute_method(params, func, response):
    start = _current_time()
    try:
        func(*params)
    except Exception as e:
        _add_exception(e, response)
    response.executionStatusResponse.executionResult.executionTime = _current_time() - start


def _add_exception(e, response):
    if os.getenv('screenshot_on_failure'):
        take_screenshot(response)
    response.executionStatusResponse.executionResult.failed = True
    response.executionStatusResponse.executionResult.errorMessage = e.__str__()
    response.executionStatusResponse.executionResult.stackTrace = traceback.format_exc()
    response.executionStatusResponse.executionResult.errorType = ProtoExecutionResult.ASSERTION


def take_screenshot(response):
    temp_file = os.path.join(tempfile.gettempdir(), "screenshot.png")
    call(["gauge_screenshot", temp_file])
    _file = open(temp_file, 'r')
    response.executionStatusResponse.executionResult.screenShot = _file.read()
    _file.close()
