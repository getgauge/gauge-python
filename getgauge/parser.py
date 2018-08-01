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
        '''
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        return PythonFile.Klass.parse(file_path, content)

    @staticmethod
    def selectPythonFileParser(parser=None):
        if parser == 'redbaron' or os.environ.get('GETGAUGE_USE_0_3_3_PARSER'):
            PythonFile.Klass = RedbaronPythonFile
        else:
            PythonFile.Klass = ParsoPythonFile


# Select the default implementation
PythonFile.selectPythonFileParser()


class PythonFileABC(six.with_metaclass(ABCMeta)):
    @staticmethod
    def parse(file_path, content=None):
        '''
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        '''
        raise NotImplementedError

    @abstractmethod
    def iter_steps(self):
        '''Iterate over steps in the parsed file'''
        raise NotImplementedError

    @abstractmethod
    def refactor_step(self, old_text, new_text, move_param_from_idx):
        '''
        Find the step with old_text and change it to new_text. The step function
        parameters are also changed accoring to move_param_from_idx. Each entry in
        this list should specify parameter position from old
        '''
        raise NotImplementedError

    @abstractmethod
    def get_code(self):
        '''Returns current content of the tree.'''
        raise NotImplementedError


# Verify that implemetations are subclasses of ABC
PythonFileABC.register(ParsoPythonFile)
PythonFileABC.register(RedbaronPythonFile)
