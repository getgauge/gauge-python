
from getgauge import logger, processor
from getgauge.messages import runner_pb2_grpc
from getgauge.messages.messages_pb2 import Empty


class RunnerServiceHandler(runner_pb2_grpc.RunnerServicer):

    def __init__(self, server):
        self.server = server

    def SuiteDataStoreInit(self, request, context):
        return processor.process_suite_data_store_init_request()

    def ExecutionStarting(self, request, context):
        return processor.process_execution_starting_reqeust(request)

    def SpecDataStoreInit(self, request, context):
        return processor.process_spec_data_store_init_request()

    def SpecExecutionStarting(self, request, context):
        return processor.process_spec_execution_starting_request(request)

    def ScenarioDataStoreInit(self, request, context):
        return processor.process_scenario_data_store_init_request()

    def ScenarioExecutionStarting(self, request, context):
        return processor.process_scenario_execution_starting_request(request)

    def StepExecutionStarting(self, request, context):
        return processor.process_step_execution_starting_request(request)

    def ExecuteStep(self, request, context):
        return processor.process_execute_step_request(request)

    def StepExecutionEnding(self, request, context):
        return processor.process_step_execution_ending_request(request)

    def ScenarioExecutionEnding(self, request, context):
        return processor.process_scenario_execution_ending_request(request)

    def SpecExecutionEnding(self, request, context):
        return processor.process_spec_execution_ending_request(request)

    def ExecutionEnding(self, request, context):
        return processor.process_execution_ending_request(request)

    def GetStepNames(self, request, context):
        return processor.process_step_names_request()

    def CacheFile(self, request, context):
        return processor.process_cache_file_request(request)

    def GetStepPositions(self, request, context):
        return processor.prceoss_step_positions_request(request)

    def GetImplementationFiles(self, request, context):
        return processor.process_impl_files_request()

    def ImplementStub(self, request, context):
        return processor.process_stub_impl_request(request)

    def ValidateStep(self, request, context):
        return processor.process_validate_step_request(request)

    def Refactor(self, request, context):
        return processor.process_refactor_request(request)

    def GetStepName(self, request, context):
        return processor.process_step_name_request(request)

    def GetGlobPatterns(self, request, context):
        return processor.process_glob_pattern_request(request)

    def KillProcess(self, request, context):
        logger.debug("KillProcessrequest received")
        logger.debug("Stoping gRPC server")
        self.server.stop(0)
        return Empty()
