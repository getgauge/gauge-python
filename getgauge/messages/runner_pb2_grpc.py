# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import getgauge.messages.messages_pb2 as messages__pb2
import grpc


class RunnerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ValidateStep = channel.unary_unary(
        '/gauge.messages.Runner/ValidateStep',
        request_serializer=messages__pb2.StepValidateRequest.SerializeToString,
        response_deserializer=messages__pb2.StepValidateResponse.FromString,
        )
    self.SuiteDataStoreInit = channel.unary_unary(
        '/gauge.messages.Runner/SuiteDataStoreInit',
        request_serializer=messages__pb2.Empty.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ExecutionStarting = channel.unary_unary(
        '/gauge.messages.Runner/ExecutionStarting',
        request_serializer=messages__pb2.ExecutionStartingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.SpecDataStoreInit = channel.unary_unary(
        '/gauge.messages.Runner/SpecDataStoreInit',
        request_serializer=messages__pb2.Empty.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.SpecExecutionStarting = channel.unary_unary(
        '/gauge.messages.Runner/SpecExecutionStarting',
        request_serializer=messages__pb2.SpecExecutionStartingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ScenarioDataStoreInit = channel.unary_unary(
        '/gauge.messages.Runner/ScenarioDataStoreInit',
        request_serializer=messages__pb2.Empty.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ScenarioExecutionStarting = channel.unary_unary(
        '/gauge.messages.Runner/ScenarioExecutionStarting',
        request_serializer=messages__pb2.ScenarioExecutionStartingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.StepExecutionStarting = channel.unary_unary(
        '/gauge.messages.Runner/StepExecutionStarting',
        request_serializer=messages__pb2.StepExecutionStartingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ExecuteStep = channel.unary_unary(
        '/gauge.messages.Runner/ExecuteStep',
        request_serializer=messages__pb2.ExecuteStepRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.StepExecutionEnding = channel.unary_unary(
        '/gauge.messages.Runner/StepExecutionEnding',
        request_serializer=messages__pb2.StepExecutionEndingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ScenarioExecutionEnding = channel.unary_unary(
        '/gauge.messages.Runner/ScenarioExecutionEnding',
        request_serializer=messages__pb2.ScenarioExecutionEndingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.SpecExecutionEnding = channel.unary_unary(
        '/gauge.messages.Runner/SpecExecutionEnding',
        request_serializer=messages__pb2.SpecExecutionEndingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.ExecutionEnding = channel.unary_unary(
        '/gauge.messages.Runner/ExecutionEnding',
        request_serializer=messages__pb2.ExecutionEndingRequest.SerializeToString,
        response_deserializer=messages__pb2.ExecutionStatusResponse.FromString,
        )
    self.GetStepNames = channel.unary_unary(
        '/gauge.messages.Runner/GetStepNames',
        request_serializer=messages__pb2.StepNamesRequest.SerializeToString,
        response_deserializer=messages__pb2.StepNamesResponse.FromString,
        )
    self.CacheFile = channel.unary_unary(
        '/gauge.messages.Runner/CacheFile',
        request_serializer=messages__pb2.CacheFileRequest.SerializeToString,
        response_deserializer=messages__pb2.Empty.FromString,
        )
    self.GetStepPositions = channel.unary_unary(
        '/gauge.messages.Runner/GetStepPositions',
        request_serializer=messages__pb2.StepPositionsRequest.SerializeToString,
        response_deserializer=messages__pb2.StepPositionsResponse.FromString,
        )
    self.GetImplementationFiles = channel.unary_unary(
        '/gauge.messages.Runner/GetImplementationFiles',
        request_serializer=messages__pb2.Empty.SerializeToString,
        response_deserializer=messages__pb2.ImplementationFileListResponse.FromString,
        )
    self.ImplementStub = channel.unary_unary(
        '/gauge.messages.Runner/ImplementStub',
        request_serializer=messages__pb2.StubImplementationCodeRequest.SerializeToString,
        response_deserializer=messages__pb2.FileDiff.FromString,
        )
    self.GetStepName = channel.unary_unary(
        '/gauge.messages.Runner/GetStepName',
        request_serializer=messages__pb2.StepNameRequest.SerializeToString,
        response_deserializer=messages__pb2.StepNameResponse.FromString,
        )
    self.GetGlobPatterns = channel.unary_unary(
        '/gauge.messages.Runner/GetGlobPatterns',
        request_serializer=messages__pb2.Empty.SerializeToString,
        response_deserializer=messages__pb2.ImplementationFileGlobPatternResponse.FromString,
        )
    self.Refactor = channel.unary_unary(
        '/gauge.messages.Runner/Refactor',
        request_serializer=messages__pb2.RefactorRequest.SerializeToString,
        response_deserializer=messages__pb2.RefactorResponse.FromString,
        )
    self.KillProcess = channel.unary_unary(
        '/gauge.messages.Runner/KillProcess',
        request_serializer=messages__pb2.KillProcessRequest.SerializeToString,
        response_deserializer=messages__pb2.Empty.FromString,
        )


class RunnerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def ValidateStep(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SuiteDataStoreInit(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ExecutionStarting(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SpecDataStoreInit(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SpecExecutionStarting(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ScenarioDataStoreInit(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ScenarioExecutionStarting(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StepExecutionStarting(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ExecuteStep(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StepExecutionEnding(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ScenarioExecutionEnding(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SpecExecutionEnding(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ExecutionEnding(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetStepNames(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CacheFile(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetStepPositions(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetImplementationFiles(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ImplementStub(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetStepName(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetGlobPatterns(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Refactor(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def KillProcess(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RunnerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ValidateStep': grpc.unary_unary_rpc_method_handler(
          servicer.ValidateStep,
          request_deserializer=messages__pb2.StepValidateRequest.FromString,
          response_serializer=messages__pb2.StepValidateResponse.SerializeToString,
      ),
      'SuiteDataStoreInit': grpc.unary_unary_rpc_method_handler(
          servicer.SuiteDataStoreInit,
          request_deserializer=messages__pb2.Empty.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ExecutionStarting': grpc.unary_unary_rpc_method_handler(
          servicer.ExecutionStarting,
          request_deserializer=messages__pb2.ExecutionStartingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'SpecDataStoreInit': grpc.unary_unary_rpc_method_handler(
          servicer.SpecDataStoreInit,
          request_deserializer=messages__pb2.Empty.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'SpecExecutionStarting': grpc.unary_unary_rpc_method_handler(
          servicer.SpecExecutionStarting,
          request_deserializer=messages__pb2.SpecExecutionStartingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ScenarioDataStoreInit': grpc.unary_unary_rpc_method_handler(
          servicer.ScenarioDataStoreInit,
          request_deserializer=messages__pb2.Empty.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ScenarioExecutionStarting': grpc.unary_unary_rpc_method_handler(
          servicer.ScenarioExecutionStarting,
          request_deserializer=messages__pb2.ScenarioExecutionStartingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'StepExecutionStarting': grpc.unary_unary_rpc_method_handler(
          servicer.StepExecutionStarting,
          request_deserializer=messages__pb2.StepExecutionStartingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ExecuteStep': grpc.unary_unary_rpc_method_handler(
          servicer.ExecuteStep,
          request_deserializer=messages__pb2.ExecuteStepRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'StepExecutionEnding': grpc.unary_unary_rpc_method_handler(
          servicer.StepExecutionEnding,
          request_deserializer=messages__pb2.StepExecutionEndingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ScenarioExecutionEnding': grpc.unary_unary_rpc_method_handler(
          servicer.ScenarioExecutionEnding,
          request_deserializer=messages__pb2.ScenarioExecutionEndingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'SpecExecutionEnding': grpc.unary_unary_rpc_method_handler(
          servicer.SpecExecutionEnding,
          request_deserializer=messages__pb2.SpecExecutionEndingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'ExecutionEnding': grpc.unary_unary_rpc_method_handler(
          servicer.ExecutionEnding,
          request_deserializer=messages__pb2.ExecutionEndingRequest.FromString,
          response_serializer=messages__pb2.ExecutionStatusResponse.SerializeToString,
      ),
      'GetStepNames': grpc.unary_unary_rpc_method_handler(
          servicer.GetStepNames,
          request_deserializer=messages__pb2.StepNamesRequest.FromString,
          response_serializer=messages__pb2.StepNamesResponse.SerializeToString,
      ),
      'CacheFile': grpc.unary_unary_rpc_method_handler(
          servicer.CacheFile,
          request_deserializer=messages__pb2.CacheFileRequest.FromString,
          response_serializer=messages__pb2.Empty.SerializeToString,
      ),
      'GetStepPositions': grpc.unary_unary_rpc_method_handler(
          servicer.GetStepPositions,
          request_deserializer=messages__pb2.StepPositionsRequest.FromString,
          response_serializer=messages__pb2.StepPositionsResponse.SerializeToString,
      ),
      'GetImplementationFiles': grpc.unary_unary_rpc_method_handler(
          servicer.GetImplementationFiles,
          request_deserializer=messages__pb2.Empty.FromString,
          response_serializer=messages__pb2.ImplementationFileListResponse.SerializeToString,
      ),
      'ImplementStub': grpc.unary_unary_rpc_method_handler(
          servicer.ImplementStub,
          request_deserializer=messages__pb2.StubImplementationCodeRequest.FromString,
          response_serializer=messages__pb2.FileDiff.SerializeToString,
      ),
      'GetStepName': grpc.unary_unary_rpc_method_handler(
          servicer.GetStepName,
          request_deserializer=messages__pb2.StepNameRequest.FromString,
          response_serializer=messages__pb2.StepNameResponse.SerializeToString,
      ),
      'GetGlobPatterns': grpc.unary_unary_rpc_method_handler(
          servicer.GetGlobPatterns,
          request_deserializer=messages__pb2.Empty.FromString,
          response_serializer=messages__pb2.ImplementationFileGlobPatternResponse.SerializeToString,
      ),
      'Refactor': grpc.unary_unary_rpc_method_handler(
          servicer.Refactor,
          request_deserializer=messages__pb2.RefactorRequest.FromString,
          response_serializer=messages__pb2.RefactorResponse.SerializeToString,
      ),
      'KillProcess': grpc.unary_unary_rpc_method_handler(
          servicer.KillProcess,
          request_deserializer=messages__pb2.KillProcessRequest.FromString,
          response_serializer=messages__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'gauge.messages.Runner', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
