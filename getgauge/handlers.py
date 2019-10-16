import threading

from getgauge import logger, processor, refactor, validator
from getgauge.messages import runner_pb2_grpc
from getgauge.messages.messages_pb2 import (
    Empty, ImplementationFileGlobPatternResponse,
    ImplementationFileListResponse, Message, StepNamesResponse)
from getgauge.registry import registry
from getgauge.util import get_impl_files, get_step_impl_dirs


class RunnerServiceHandler(runner_pb2_grpc.RunnerServicer):

    def __init__(self, server):
        self.server = server
        self.kill_event = threading.Event()

    def SuiteDataStoreInit(self, request, context):
        res = Message()
        processor.init_suite_data_store(request, res)
        return res.executionStatusResponse

    def ExecutionStarting(self, request, context):
        res = Message()
        processor.execute_before_suite_hook(request, res)
        return res.executionStatusResponse

    def SpecDataStoreInit(self, request, context):
        res = Message()
        processor.init_spec_data_store(request, res)
        return res.executionStatusResponse

    def SpecExecutionStarting(self, request, context):
        res = Message()
        processor.execute_before_spec_hook(request, res)
        return res.executionStatusResponse

    def ScenarioDataStoreInit(self, request, context):
        res = Message()
        processor.init_scenario_data_store(request, res)
        return res.executionStatusResponse

    def ScenarioExecutionStarting(self, request, context):
        res = Message()
        processor.execute_before_scenario_hook(request, res)
        return res.executionStatusResponse

    def StepExecutionStarting(self, request, context):
        res = Message()
        processor.execute_before_step_hook(request, res)
        return res.executionStatusResponse

    def ExecuteStep(self, request, context):
        res = Message()
        processor.execute_step(request, res)
        return res.executionStatusResponse

    def StepExecutionEnding(self, request, context):
        res = Message()
        processor.execute_after_step_hook(request, res)
        return res.executionStatusResponse

    def ScenarioExecutionEnding(self, request, context):
        res = Message()
        processor.execute_after_scenario_hook(request, res)
        return res.executionStatusResponse

    def SpecExecutionEnding(self, request, context):
        res = Message()
        processor.execute_after_spec_hook(request, res)
        return res.executionStatusResponse

    def ExecutionEnding(self, request, context):
        res = Message()
        processor.execute_after_suite_hook(request, res)
        return res.executionStatusResponse

    def GetStepNames(self, request, context):
        res = StepNamesResponse()
        res.steps.extend(registry.steps())
        return res

    def CacheFile(self, request, context):
        processor.cache_file(request, None)
        return Empty()

    def GetStepPositions(self, request, context):
        res = Message()
        processor.step_positions_response(request.filePath, res)
        return res.stepPositionsResponse

    def GetImplementationFiles(self, request, context):
        res = ImplementationFileListResponse()
        res.implementationFilePaths.extend(get_impl_files())
        return res

    def ImplementStub(self, request, context):
        res = Message()
        processor.stub_impl_response(
            request.codes, request.implementationFilePath, res)
        return res.fileDiff

    def ValidateStep(self, request, context):
        res = Message()
        validator.validate_step(request, res)
        return res.stepValidateResponse

    def Refactor(self, request, context, with_location=True):
        res = Message()
        refactor.refactor_step(request, res, with_location)
        return res.refactorResponse

    def GetStepName(self, request, context):
        res = Message()
        info = registry.get_info_for(request.stepValue)
        processor.step_name_response(info, res)
        return res.stepNameResponse

    def GetGlobPatterns(self, request, context):
        res = ImplementationFileGlobPatternResponse()
        globPatterns = [["{}/**/*.py".format(d)] for d in get_step_impl_dirs()]
        res.globPatterns.extend(
            [item for sublist in globPatterns for item in sublist])
        return res

    def KillProcess(self, request, context):
        self.server.stop(0)
        self.kill_event.set()
        return Empty()

    def wait_till_terminated(self):
        self.kill_event.wait()
        exit(0)
