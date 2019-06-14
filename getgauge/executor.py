import inspect
import os
import sys
import time
import traceback

from getgauge.messages.messages_pb2 import Message
from getgauge.messages.spec_pb2 import ProtoExecutionResult
from getgauge.registry import registry, MessagesStore, ScreenshotsStore


def set_response_values(request, response):
    response.messageType = Message.ExecutionStatusResponse
    response.executionStatusResponse.executionResult.failed = False
    response.executionStatusResponse.executionResult.executionTime = 0


def run_hook(request, response, hooks, execution_info):
    set_response_values(request, response)
    for hook in hooks:
        execute_method([execution_info], hook, response)


def _false(func, exception): return False


def execute_method(params, step, response, is_continue_on_failure=_false):
    start = _current_time()
    try:
        params = _get_args(params, step)
        step.impl(*params)
    except Exception as e:
        _add_exception(e, response, is_continue_on_failure(step.impl, e))
    response.executionStatusResponse.executionResult.executionTime = _current_time() - start
    response.executionStatusResponse.executionResult.message.extend(MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(ScreenshotsStore.pending_screenshots())


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
        screenshot = registry.screenshot_provider()()
        response.executionStatusResponse.executionResult.screenShot = screenshot
        response.executionStatusResponse.executionResult.failureScreenshot = screenshot
    response.executionStatusResponse.executionResult.failed = True
    message = e.__str__()
    if not message:
        message = "Exception occurred"
    response.executionStatusResponse.executionResult.errorMessage = message
    response.executionStatusResponse.executionResult.stackTrace = traceback.format_exc()
    response.executionStatusResponse.executionResult.errorType = ProtoExecutionResult.ASSERTION
    if continue_on_failure:
        response.executionStatusResponse.executionResult.recoverableError = True
    response.executionStatusResponse.executionResult.message.extend(MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(ScreenshotsStore.pending_screenshots())
