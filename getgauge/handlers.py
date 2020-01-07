import threading
import time

from getgauge import logger, processor
from getgauge.messages import services_pb2_grpc as sp
from getgauge.messages.messages_pb2 import Empty

kill_event = threading.Event()


class GrpcServiceHandler(sp.RunnerServicer):

    def __init__(self, server):
        self.server = server
        self.kill_event = threading.Event()

    def InitializeSuiteDataStore(self, request, context):
        return processor.process_suite_data_store_init_request()

    def StartExecution(self, request, context):
        return processor.process_execution_starting_request(request)

    def InitializeSpecDataStore(self, request, context):
        return processor.process_spec_data_store_init_request()

    def StartSpecExecution(self, request, context):
        return processor.process_spec_execution_starting_request(request)

    def InitializeScenarioDataStore(self, request, context):
        return processor.process_scenario_data_store_init_request()

    def StartScenarioExecution(self, request, context):
        return processor.process_scenario_execution_starting_request(request)

    def StartStepExecution(self, request, context):
        return processor.process_step_execution_starting_request(request)

    def ExecuteStep(self, request, context):
        return processor.process_execute_step_request(request)

    def FinishStepExecution(self, request, context):
        return processor.process_step_execution_ending_request(request)

    def FinishScenarioExecution(self, request, context):
        return processor.process_scenario_execution_ending_request(request)

    def FinishSpecExecution(self, request, context):
        return processor.process_spec_execution_ending_request(request)

    def FinishExecution(self, request, context):
        return processor.process_execution_ending_request(request)

    def CacheFile(self, request, context):
        return processor.process_cache_file_request(request)

    def GetStepName(self, request, context):
        return processor.process_step_name_request(request)

    def GetGlobPatterns(self, request, context):
        return processor.process_glob_pattern_request(request)

    def GetStepNames(self, request, context):
        return processor.process_step_names_request()

    def GetStepPositions(self, request, context):
        return processor.process_step_positions_request(request)

    def GetImplementationFiles(self, request, context):
        return processor.process_impl_files_request()

    def ImplementStub(self, request, context):
        return processor.process_stub_impl_request(request)

    def Refactor(self, request, context):
        return processor.process_refactor_request(request)

    def ValidateStep(self, request, context):
        return processor.process_validate_step_request(request)

    def Kill(self, request, context):
        logger.debug("KillProcessrequest received")
        self.kill_event.set()
        return Empty()

    def wait_for_kill_event(self):
        self.kill_event.wait()
        time.sleep(0.5)
        self.server.stop(0)
        exit(0)
