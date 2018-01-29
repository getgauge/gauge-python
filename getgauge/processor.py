import sys

from os import path

from getgauge.connection import read_message, send_message
from getgauge.executor import set_response_values, execute_method, run_hook
from getgauge.impl_loader import load_impls
from getgauge.messages.messages_pb2 import Message, StepPositionsResponse
from getgauge.messages.spec_pb2 import Parameter, Span
from getgauge.python import Table, create_execution_context_from, DataStoreFactory
from getgauge.refactor import refactor_step
from getgauge.registry import registry, _MessagesStore
from getgauge.util import get_step_impl_dir
from getgauge.validator import validate_step
from getgauge.static_loader import reload_steps


def _validate_step(request, response, socket):
    validate_step(request, response)


def _send_step_name(request, response, socket):
    response.messageType = Message.StepNameResponse
    info = registry.get_info_for(request.stepNameRequest.stepValue)
    response.stepNameResponse.isStepPresent = False
    if info.step_text is not None:
        response.stepNameResponse.isStepPresent = True
        response.stepNameResponse.stepName.append(info.step_text)
        response.stepNameResponse.fileName = info.file_name
        response.stepNameResponse.span.start = info.span['start']
        response.stepNameResponse.span.startChar = info.span['startChar']
        response.stepNameResponse.span.end = info.span['end']
        response.stepNameResponse.span.endChar = info.span['endChar']
    response.stepNameResponse.hasAlias = info.has_alias


def _refactor(request, response, socket):
    response.messageType = Message.RefactorResponse
    try:
        refactor_step(request, response)
    except Exception as e:
        response.refactorResponse.success = False
        response.refactorResponse.error = 'Reason: {}'.format(e.__str__())


def _send_all_step_names(request, response, socket):
    response.messageType = Message.StepNamesResponse
    response.stepNamesResponse.steps.extend(registry.steps())


def _execute_step(request, response, socket):
    params = []
    for p in request.executeStepRequest.parameters:
        params.append(Table(p.table) if p.parameterType in [Parameter.Table, Parameter.Special_Table] else p.value)
    set_response_values(request, response)
    impl = registry.get_info_for(request.executeStepRequest.parsedStepText).impl
    execute_method(params, impl, response, registry.is_continue_on_failure)


def _execute_before_suite_hook(request, response, socket, clear=True):
    if clear:
        registry.clear()
        load_impls(get_step_impl_dir())
    execution_info = create_execution_context_from(request.executionStartingRequest.currentExecutionInfo)
    run_hook(request, response, registry.before_suite(), execution_info)


def _execute_after_suite_hook(request, response, socket):
    execution_info = create_execution_context_from(request.executionEndingRequest.currentExecutionInfo)
    run_hook(request, response, registry.after_suite(), execution_info)


def _execute_before_spec_hook(request, response, socket):
    execution_info = create_execution_context_from(request.specExecutionStartingRequest.currentExecutionInfo)
    run_hook(request, response, registry.before_spec(execution_info.specification.tags), execution_info)


def _execute_after_spec_hook(request, response, socket):
    execution_info = create_execution_context_from(request.specExecutionEndingRequest.currentExecutionInfo)
    run_hook(request, response, registry.after_spec(execution_info.specification.tags), execution_info)


def _execute_before_scenario_hook(request, response, socket):
    execution_info = create_execution_context_from(request.scenarioExecutionStartingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + list(execution_info.specification.tags)
    run_hook(request, response, registry.before_scenario(tags), execution_info)


def _execute_after_scenario_hook(request, response, socket):
    execution_info = create_execution_context_from(request.scenarioExecutionEndingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + list(execution_info.specification.tags)
    run_hook(request, response, registry.after_scenario(tags), execution_info)


def _execute_before_step_hook(request, response, socket):
    _MessagesStore.clear()
    execution_info = create_execution_context_from(request.stepExecutionStartingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + list(execution_info.specification.tags)
    run_hook(request, response, registry.before_step(tags), execution_info)


def _execute_after_step_hook(request, response, socket):
    execution_info = create_execution_context_from(request.stepExecutionEndingRequest.currentExecutionInfo)
    tags = list(execution_info.scenario.tags) + list(execution_info.specification.tags)
    run_hook(request, response, registry.after_step(tags), execution_info)
    response.executionStatusResponse.executionResult.message.extend(_MessagesStore.pending_messages())


def _init_scenario_data_store(request, response, socket):
    DataStoreFactory.scenario_data_store().clear()
    set_response_values(request, response)


def _init_spec_data_store(request, response, socket):
    DataStoreFactory.spec_data_store().clear()
    set_response_values(request, response)


def _init_suite_data_store(request, response, socket):
    DataStoreFactory.suite_data_store().clear()
    set_response_values(request, response)


def _load_from_disk(file_path):
    if path.isfile(file_path):
        f = open(file_path, 'r+')
        reload_steps(f.read(), file_path)
        f.close()
    else:
        registry.remove_steps(file_path)


def _cache_file(request, response, socket):
    if not request.cacheFileRequest.isClosed:
        reload_steps(request.cacheFileRequest.content, request.cacheFileRequest.filePath)
    else:
        _load_from_disk(request.cacheFileRequest.filePath)


def _step_positions(request, response, socket):
    positions = registry.get_step_positions(request.stepPositionsRequest.filePath)
    create_pos = lambda p: StepPositionsResponse.StepPosition(
        **{'stepValue': p['stepValue'], 'span': Span(**p['span'])})
    response.messageType = Message.StepPositionsResponse
    response.stepPositionsResponse.stepPositions.extend([create_pos(x) for x in positions])


def _kill_runner(request, response, socket):
    socket.close()
    sys.exit()


processors = {Message.ExecutionStarting: _execute_before_suite_hook,
              Message.ExecutionEnding: _execute_after_suite_hook,
              Message.SpecExecutionStarting: _execute_before_spec_hook,
              Message.SpecExecutionEnding: _execute_after_spec_hook,
              Message.ScenarioExecutionStarting: _execute_before_scenario_hook,
              Message.ScenarioExecutionEnding: _execute_after_scenario_hook,
              Message.StepExecutionStarting: _execute_before_step_hook,
              Message.StepExecutionEnding: _execute_after_step_hook,
              Message.ExecuteStep: _execute_step,
              Message.StepValidateRequest: _validate_step,
              Message.StepNamesRequest: _send_all_step_names,
              Message.ScenarioDataStoreInit: _init_scenario_data_store,
              Message.SpecDataStoreInit: _init_spec_data_store,
              Message.SuiteDataStoreInit: _init_suite_data_store,
              Message.StepNameRequest: _send_step_name,
              Message.RefactorRequest: _refactor,
              Message.CacheFileRequest: _cache_file,
              Message.StepPositionsRequest: _step_positions,
              Message.KillProcessRequest: _kill_runner,
              }


def dispatch_messages(socket):
    while True:
        request = read_message(socket, Message())
        response = Message()
        processors[request.messageType](request, response, socket)
        if request.messageType != Message.CacheFileRequest:
            send_message(response, request, socket)
