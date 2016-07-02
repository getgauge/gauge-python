from getgauge.messages.messages_pb2 import Message, StepValidateResponse
from getgauge.registry import registry


def validate_step(request, response):
    response.messageType = Message.StepValidateResponse
    response.stepValidateResponse.isValid = True
    if registry.is_step_implemented(request.stepValidateRequest.stepText) is False:
        response.stepValidateResponse.errorType = StepValidateResponse.STEP_IMPLEMENTATION_NOT_FOUND
        response.stepValidateResponse.errorMessage = 'Step implementation not found'
        response.stepValidateResponse.isValid = False
    elif registry.has_multiple_impls(request.stepValidateRequest.stepText):
        response.stepValidateResponse.isValid = False
        response.stepValidateResponse.errorType = StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION
        response.stepValidateResponse.errorMessage = 'Multiple implementation found for `{}` ({})'. \
            format(request.stepValidateRequest.stepText, ', '.join(
            ['{}:{}'.format(impl.file_name, impl.line_number) for impl in
             registry.get_infos(request.stepValidateRequest.stepText)]))
