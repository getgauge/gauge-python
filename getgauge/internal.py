from collections import namedtuple

Span = namedtuple('Span', 'start startChar end endChar')
FunctionSteps = namedtuple('FunctionSteps', 'steps func file_path span')

ContentDiff = namedtuple('ContentDiff', 'span content')
RefactorDiff = namedtuple('RefactorDiff', 'step params')

EmptyContentDiff = ContentDiff(span=Span(0, 0, 0, 0), content='')