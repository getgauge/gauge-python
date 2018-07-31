from collections import namedtuple

Span = namedtuple('Span', 'start startChar end endChar')
FunctionSteps = namedtuple('FunctionSteps', 'steps func file_path span')
