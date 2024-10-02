from getgauge.exceptions import MultipleImplementationFoundException
from getgauge.messages.messages_pb2 import TextDiff
from getgauge.messages.spec_pb2 import Span
from getgauge.parser import Parser
from getgauge.registry import registry


def refactor_step(request, response):
    if registry.has_multiple_impls(request.oldStepValue.stepValue):
        raise MultipleImplementationFoundException('Multiple Implementation found for `{}`'.format(
            request.oldStepValue.parameterizedStepValue
        ))
    info = registry.get_info_for(request.oldStepValue.stepValue)
    impl_file = Parser.parse(info.file_name)
    diffs = impl_file.refactor_step(
        info.step_text,
        request.newStepValue.parameterizedStepValue,
        _new_parameter_positions(request),
    )
    content = impl_file.get_code()
    if request.saveChanges:
        with open(info.file_name, 'w', encoding="utf-8") as f:
            f.write(content)
    response.success = True
    response.filesChanged.append(info.file_name)
    response.fileChanges.add(
        fileName=info.file_name,
        fileContent=content,  # FIXME: Remove deprecated field
        diffs=[TextDiff(span=Span(**d[0]), content=d[1]) for d in diffs],
    )


def _new_parameter_positions(request):
    moved_pos = list(range(len(request.paramPositions)))
    for position in request.paramPositions:
        moved_pos[position.newPosition] = position.oldPosition
    return moved_pos
