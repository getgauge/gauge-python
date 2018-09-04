import threading
from getgauge import processor, validator, refactor
from getgauge.messages import lsp_pb2_grpc
from getgauge.messages.lsp_pb2 import Empty
from getgauge.messages.messages_pb2 import Message, \
    ImplementationFileGlobPatternResponse, StepNamesResponse, \
    ImplementationFileListResponse
from getgauge.registry import registry
from getgauge.util import get_impl_files, get_step_impl_dir


class LspServerHandler(lsp_pb2_grpc.lspServiceServicer):

    def __init__(self, server):
        self.server = server
        self.kill_event = threading.Event()

    def GetStepNames(self, request, context):
        res = StepNamesResponse()
        res.steps.extend(registry.steps())
        return res

    def CacheFile(self, request, context):
        file = request.filePath
        status = request.status
        processor.update_registry(file, status, request.content)
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
        res.globPatterns.extend(["{}/**/*.py".format(get_step_impl_dir())])
        return res

    def KillProcess(self, request, context):
        self.server.stop(0)
        self.kill_event.set()
        return Empty()

    def wait_till_terminated(self):
        self.kill_event.wait()
        exit(0)
