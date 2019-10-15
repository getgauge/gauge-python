import os
import traceback
from os import environ, path
from threading import Timer

import ptvsd
from getgauge import logger
from getgauge.executor import execute_method, run_hook, set_response_values
from getgauge.impl_loader import load_impls
from getgauge.messages.messages_pb2 import (CacheFileRequest, Message,
                                            StepPositionsResponse, TextDiff)
from getgauge.messages.spec_pb2 import Parameter, Span
from getgauge.python import Table, create_execution_context_from, data_store
from getgauge.refactor import refactor_step
from getgauge.registry import MessagesStore, ScreenshotsStore, registry
from getgauge.static_loader import reload_steps
from getgauge.util import (get_file_name, get_impl_files, get_step_impl_dirs,
                           read_file_contents)
from getgauge.validator import validate_step as _validate_step

ATTACH_DEBUGGER_EVENT = 'Runner Ready for Debugging'


def validate_step(request, response):
    _validate_step(request.stepValidateRequest, response)


def send_step_name(request, response):
    response.messageType = Message.StepNameResponse
    info = registry.get_info_for(request.stepNameRequest.stepValue)
    step_name_response(info, response)


def step_name_response(info, response):
    response.stepNameResponse.isStepPresent = False
    if info.step_text is not None:
        response.stepNameResponse.isStepPresent = True
        if info.has_alias:
            for alias in info.aliases:
                response.stepNameResponse.stepName.append(alias)
        else:
            response.stepNameResponse.stepName.append(info.step_text)
        response.stepNameResponse.fileName = info.file_name
        response.stepNameResponse.span.start = info.span['start']
        response.stepNameResponse.span.startChar = info.span['startChar']
        response.stepNameResponse.span.end = info.span['end']
        response.stepNameResponse.span.endChar = info.span['endChar']
    response.stepNameResponse.hasAlias = info.has_alias


def refactor(request, response):
    response.messageType = Message.RefactorResponse
    try:
        refactor_step(request.refactorRequest, response)
    except Exception as e:
        response.refactorResponse.success = False
        response.refactorResponse.error = 'Reason: {}'.format(e.__str__())


def send_all_step_names(_request, response):
    response.messageType = Message.StepNamesResponse
    response.stepNamesResponse.steps.extend(registry.steps())


def execute_step(request, response):
    params = []
    for p in request.executeStepRequest.parameters:
        params.append(Table(p.table) if p.parameterType in [
            Parameter.Table, Parameter.Special_Table] else p.value)
    set_response_values(request, response)
    info = registry.get_info_for(request.executeStepRequest.parsedStepText)
    execute_method(params, info, response, registry.is_continue_on_failure)


def handle_detached():
    logger.info("No debugger attached. Stopping the execution.")
    os._exit(1)


def execute_before_suite_hook(request, response, clear=True):
    if clear:
        registry.clear()
        load_impls(get_step_impl_dirs())
    if environ.get('DEBUGGING'):
        ptvsd.enable_attach(address=(
            '127.0.0.1', int(environ.get('DEBUG_PORT'))))
        print(ATTACH_DEBUGGER_EVENT)
        t = Timer(int(environ.get("debugger_wait_time", 30)), handle_detached)
        t.start()
        ptvsd.wait_for_attach()
        t.cancel()

    execution_info = create_execution_context_from(
        request.executionStartingRequest.currentExecutionInfo)
    run_hook(request, response, registry.before_suite(), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_after_suite_hook(request, response):
    execution_info = create_execution_context_from(
        request.executionEndingRequest.currentExecutionInfo)
    run_hook(request, response, registry.after_suite(), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_before_spec_hook(request, response):
    execution_info = create_execution_context_from(
        request.specExecutionStartingRequest.currentExecutionInfo)
    run_hook(request, response, registry.before_spec(
        execution_info.specification.tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_after_spec_hook(request, response):
    execution_info = create_execution_context_from(
        request.specExecutionEndingRequest.currentExecutionInfo)
    run_hook(request, response, registry.after_spec(
        execution_info.specification.tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_before_scenario_hook(request, response):
    execution_info = create_execution_context_from(
        request.scenarioExecutionStartingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
           list(execution_info.specification.tags)
    run_hook(request, response, registry.before_scenario(tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_after_scenario_hook(request, response):
    execution_info = create_execution_context_from(
        request.scenarioExecutionEndingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    run_hook(request, response, registry.after_scenario(tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_before_step_hook(request, response):
    execution_info = create_execution_context_from(
        request.stepExecutionStartingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    run_hook(request, response, registry.before_step(tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def execute_after_step_hook(request, response):
    execution_info = create_execution_context_from(
        request.stepExecutionEndingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    run_hook(request, response, registry.after_step(tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(
        MessagesStore.pending_messages())
    response.executionStatusResponse.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def init_scenario_data_store(request, response):
    data_store.scenario.clear()
    set_response_values(request, response)


def init_spec_data_store(request, response):
    data_store.spec.clear()
    set_response_values(request, response)


def init_suite_data_store(request, response):
    data_store.suite.clear()
    set_response_values(request, response)


def _load_from_disk(file_path):
    if path.isfile(file_path):
        reload_steps(file_path)


def cache_file(request, _response):
    file = request.cacheFileRequest.filePath
    status = request.cacheFileRequest.status
    update_registry(file, status, request.cacheFileRequest.content)


def update_registry(file, status, content):
    if status == CacheFileRequest.CHANGED or status == CacheFileRequest.OPENED:
        reload_steps(file, content)
    elif status == CacheFileRequest.CREATED:
        if not registry.is_file_cached(file):
            _load_from_disk(file)
    elif status == CacheFileRequest.CLOSED:
        _load_from_disk(file)
    else:
        registry.remove_steps(file)


def _step_positions(request, response):
    file_path = request.stepPositionsRequest.filePath
    step_positions_response(file_path, response)


def step_positions_response(file_path, response):
    positions = registry.get_step_positions(file_path)
    response.messageType = Message.StepPositionsResponse
    response.stepPositionsResponse.stepPositions.extend(
        [_create_pos(x) for x in positions])


def _create_pos(p):
    return StepPositionsResponse.StepPosition(**{'stepValue': p['stepValue'], 'span': Span(**p['span'])})

def _get_impl_file_list(_request, response):
    response.messageType = Message.ImplementationFileListResponse
    files = get_impl_files()
    response.implementationFileListResponse.implementationFilePaths.extend(
        files)


def get_stub_impl_content(request, response):
    response.messageType = Message.FileDiff
    file_name = request.stubImplementationCodeRequest.implementationFilePath
    codes = request.stubImplementationCodeRequest.codes
    stub_impl_response(codes, file_name, response)


def stub_impl_response(codes, file_name, response):
    content = read_file_contents(file_name)
    prefix = ""
    if content is not None:
        new_line_char = '\n' if len(content.strip().split(
            '\n')) == len(content.split('\n')) else ''
        last_line = len(content.split('\n'))
        prefix = "from getgauge.python import step\n" if len(
            content.strip()) == 0 else new_line_char
        span = Span(**{'start': last_line, 'startChar': 0,
                       'end': last_line, 'endChar': 0})
    else:
        file_name = get_file_name()
        prefix = "from getgauge.python import step\n"
        span = Span(**{'start': 0, 'startChar': 0, 'end': 0, 'endChar': 0})
    codes = [prefix] + codes[:]
    textDiffs = [TextDiff(**{'span': span, 'content': '\n'.join(codes)})]
    response.fileDiff.filePath = file_name
    response.fileDiff.textDiffs.extend(textDiffs)


def glob_pattern(_request, response):
    patterns = [["{}/**/*.py".format(d)] for d in get_step_impl_dirs()]
    return response.implementationFileGlobPatternResponse.globPatterns.extend([item for sublist in patterns for item in sublist])
