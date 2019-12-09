import inspect
import os
import sys
import time
import traceback

from getgauge.messages.messages_pb2 import ExecutionStatusResponse, Message
from getgauge.messages.spec_pb2 import ProtoExecutionResult
from getgauge.registry import MessagesStore, ScreenshotsStore, registry


def create_execution_status_response():
    response = ExecutionStatusResponse()
    response.executionResult.failed = False
    response.executionResult.executionTime = 0
    return response


def run_hook(request, hooks, execution_info):
    response = create_execution_status_response()
    for hook in hooks:
        execute_method([execution_info], hook, response)
    return response


def _false(func, exception): return False


def execute_method(params, step, response, is_continue_on_failure=_false):
    start = _current_time()
    try:
        params = _get_args(params, step)
        step.impl(*params)
    except Exception as e:
        _add_exception(e, response, is_continue_on_failure(step.impl, e))
    response.executionResult.executionTime = _current_time() - start
    response.executionResult.message.extend(MessagesStore.pending_messages())
    response.executionResult.screenshotFiles.extend(ScreenshotsStore.pending_screenshots())


def _current_time(): return int(round(time.time() * 1000))


def _get_args(params, hook_or_step):
    _params = [hook_or_step.instance] if hook_or_step.instance is not None else []
    args_length = 0
    if sys.version_info < (3, 3):
        args_length = len(inspect.getargspec(hook_or_step.impl).args)
    else:
        args_length = len(inspect.signature(hook_or_step.impl).parameters)
    if args_length < 1:
        return []
    return (_params + params) if args_length > len(params) else params

def _add_exception(e, response, continue_on_failure):
    if os.getenv('screenshot_on_failure') == 'true':
        screenshot = ScreenshotsStore.capture_to_file()
        response.executionResult.failureScreenshotFile = screenshot
    response.executionResult.failed = True
    message = e.__str__()
    if not message:
        message = "Exception occurred"
    response.executionResult.errorMessage = message
    response.executionResult.stackTrace = traceback.format_exc()
    response.executionResult.errorType = ProtoExecutionResult.ASSERTION
    if continue_on_failure:
        response.executionResult.recoverableError = True
    response.executionResult.message.extend(MessagesStore.pending_messages())
    response.executionResult.screenshotFiles.extend(ScreenshotsStore.pending_screenshots())
