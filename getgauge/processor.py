import os
import traceback
from os import environ, path
from threading import Timer

from getgauge import logger
from getgauge.executor import (create_execution_status_response,
                               execute_method, run_hook)
from getgauge.impl_loader import load_impls
from getgauge.messages.messages_pb2 import *
from getgauge.messages.spec_pb2 import Parameter, Span
from getgauge.python import Table, create_execution_context_from, data_store
from getgauge.refactor import refactor_step
from getgauge.registry import MessagesStore, ScreenshotsStore, registry
from getgauge.static_loader import reload_steps
from getgauge.util import (get_file_name, get_impl_files, get_step_impl_dirs,
                           read_file_contents)
from getgauge.validator import validate_step

def process_validate_step_request(request):
    return validate_step(request)


def process_step_name_request(request):
    response = StepNameResponse()
    info = registry.get_info_for(request.stepValue)
    response.isStepPresent = False
    if info.step_text is not None:
        response.isStepPresent = True
        if info.has_alias:
            for alias in info.aliases:
                response.stepName.append(alias)
        else:
            response.stepName.append(info.step_text)
        response.fileName = info.file_name
        response.span.start = info.span['start']
        response.span.startChar = info.span['startChar']
        response.span.end = info.span['end']
        response.span.endChar = info.span['endChar']
    response.hasAlias = info.has_alias
    return response


def process_refactor_request(request):
    response = RefactorResponse()
    try:
        refactor_step(request, response)
    except Exception as e:
        response.success = False
        response.error = 'Reason: {}'.format(e.__str__())
    return response


def process_step_names_request():
    response = StepNamesResponse()
    response.steps.extend(registry.steps())
    return response


def process_execute_step_request(request):
    params = []
    for p in request.parameters:
        params.append(Table(p.table) if p.parameterType in [
            Parameter.Table, Parameter.Special_Table] else p.value)
    response = create_execution_status_response()
    info = registry.get_info_for(request.parsedStepText)
    execute_method(params, info, response, registry.is_continue_on_failure)
    return response


def _add_message_and_screenshots(response):
    response.executionResult.message.extend(MessagesStore.pending_messages())
    response.executionResult.screenshots.extend(
        ScreenshotsStore.pending_screenshots())


def process_execution_starting_request(request, clear=True):
    if clear:
        registry.clear()
        load_impls(get_step_impl_dirs())
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    response = run_hook(request, registry.before_suite(), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_execution_ending_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    response = run_hook(request, registry.after_suite(), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_spec_execution_starting_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    response = run_hook(request, registry.before_spec(
        execution_info.specification.tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_spec_execution_ending_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    response = run_hook(request, registry.after_spec(
        execution_info.specification.tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_scenario_execution_starting_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    response = run_hook(
        request, registry.before_scenario(tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_scenario_execution_ending_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    response = run_hook(request, registry.after_scenario(tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_step_execution_starting_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    response = run_hook(request, registry.before_step(tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_step_execution_ending_request(request):
    execution_info = create_execution_context_from(
        request.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + \
        list(execution_info.specification.tags)
    response = run_hook(request, registry.after_step(tags), execution_info)
    _add_message_and_screenshots(response)
    return response


def process_scenario_data_store_init_request():
    data_store.scenario.clear()
    return create_execution_status_response()


def process_spec_data_store_init_request():
    data_store.spec.clear()
    return create_execution_status_response()


def process_suite_data_store_init_request():
    data_store.suite.clear()
    return create_execution_status_response()


def _load_from_disk(file_path):
    if path.isfile(file_path):
        reload_steps(file_path)


def process_cache_file_request(request):
    file = request.filePath
    status = request.status
    if status == CacheFileRequest.CHANGED or status == CacheFileRequest.OPENED:
        reload_steps(file, request.content)
    elif status == CacheFileRequest.CREATED:
        if not registry.is_file_cached(file):
            _load_from_disk(file)
    elif status == CacheFileRequest.CLOSED:
        _load_from_disk(file)
    else:
        registry.remove_steps(file)
    return Empty()


def process_step_positions_request(request):
    file_path = request.filePath
    positions = registry.get_step_positions(file_path)
    response = StepPositionsResponse()
    response.stepPositions.extend([_create_pos(x) for x in positions])
    return response


def _create_pos(p):
    return StepPositionsResponse.StepPosition(**{'stepValue': p['stepValue'], 'span': Span(**p['span'])})


def process_impl_files_request():
    files = get_impl_files()
    res = ImplementationFileListResponse()
    res.implementationFilePaths.extend(files)
    return res


def process_stub_impl_request(request):
    response = FileDiff()
    file_name = request.implementationFilePath
    codes = request.codes
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
    response.filePath = file_name
    response.textDiffs.extend(textDiffs)
    return response


def process_glob_pattern_request(request):
    res = ImplementationFileGlobPatternResponse()
    globPatterns = [["{}/**/*.py".format(d)] for d in get_step_impl_dirs()]
    res.globPatterns.extend(
        [item for sublist in globPatterns for item in sublist])
    return res
