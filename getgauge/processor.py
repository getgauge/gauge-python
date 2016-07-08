import sys

from getgauge.connection import read_message, send_message
from getgauge.executor import set_response_values, execute_method, run_hook
from getgauge.messages.messages_pb2 import Message
from getgauge.messages.spec_pb2 import Parameter
from getgauge.python import Table, create_execution_context_from, DataStoreFactory
from getgauge.refactor import refactor_step
from getgauge.registry import registry, _MessagesStore
from getgauge.validator import validate_step


def _validate_step(request, response, socket):
    validate_step(request, response)


def _send_step_name(request, response, socket):
    response.messageType = Message.StepNameResponse
    info = registry.get_info(request.stepNameRequest.stepValue)
    response.stepNameResponse.isStepPresent = False
    if info.step_text is not None:
        response.stepNameResponse.isStepPresent = True
        response.stepNameResponse.stepName.append(info.step_text)
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
    response.stepNamesResponse.steps.extend(registry.all_steps())


def _execute_step(request, response, socket):
    params = []
    for param in request.executeStepRequest.parameters:
        params.append(Table(param.table)) if param.parameterType == Parameter.Table else params.append(param.value)
    set_response_values(request, response)
    impl = registry.get_info(request.executeStepRequest.parsedStepText).impl
    execute_method(params, impl, response, registry.is_continue_on_failure(impl))


def _execute_before_suite_hook(request, response, socket):
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
              Message.KillProcessRequest: _kill_runner,
              }


def dispatch_messages(socket):
    while True:
        request = read_message(socket, Message())
        response = Message()
        processors[request.messageType](request, response, socket)
        send_message(response, request, socket)
