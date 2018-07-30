import os
import sys
import six
from abc import ABCMeta, abstractmethod
from .parser_parso import ParsoPythonFile
from .parser_redbaron import RedbaronPythonFile


class PythonFile(object):
    Klass = None

    @staticmethod
    def parse(file_path, content=None):
        # type: (str, Optional[str]) -> Optional[PythonFile]
        '''
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        return PythonFile.Klass.parse(file_path, content)

    @staticmethod
    def selectPythonFileParser(parser=None):
        if parser == 'redbaron':
            PythonFile.Klass = RedbaronPythonFile
        elif parser == 'parso' or sys.hexversion > 0x3070000 or os.environ.get('GETGAUGE_USE_PARSO'):
            PythonFile.Klass = ParsoPythonFile
        else:
            PythonFile.Klass = RedbaronPythonFile


# Select the default implementation
PythonFile.selectPythonFileParser()


class PythonFileABC(six.with_metaclass(ABCMeta)):
    @staticmethod
    def parse(file_path, content=None):
        # type: (str, Optional[str]) -> Optional[PythonFileABC]
        '''
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        raise NotImplementedError

    @abstractmethod
    def iter_steps(self):
        # type: () -> Generator[FunctionSteps]
        '''Iterate over steps in the parsed file'''
        raise NotImplementedError

    @abstractmethod
    def refactor_step(self, old_text, new_text, move_param_from_idx):
        # type: (str, str, List[int]) -> List[Tuple[Span, str]]
        '''
        Find the step with old_text and change it to new_text. The step function
        parameters are also changed accoring to move_param_from_idx. Each entry in
        this list should specify parameter position from old
        '''
        raise NotImplementedError

    @abstractmethod
    def get_code(self):
        # type: () -> str
        '''Returns current content of the tree.'''
        raise NotImplementedError

    @abstractmethod
    def save(self, new_path=None):
        # type: (Optional[str])
        '''Saves the tree to specified path or file_path'''
        raise NotImplementedError


# Verify that implemetations are subclasses of ABC
PythonFileABC.register(ParsoPythonFile)
PythonFileABC.register(RedbaronPythonFile)
