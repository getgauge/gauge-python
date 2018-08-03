import os
import six
from abc import ABCMeta, abstractmethod
from getgauge.parser_parso import ParsoPythonFile
from getgauge.parser_redbaron import RedbaronPythonFile


class PythonFile(object):
    Class = None

    @staticmethod
    def parse(file_path, content=None):
        """
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        """
        return PythonFile.Class.parse(file_path, content)

    @staticmethod
    def select_python_parser(parser=None):
        """
        Select default parser for loading and refactoring steps. Passing `redbaron` as argument
        will select the old paring engine from v0.3.3

        Replacing the redbaron parser was necessary to support Python 3 syntax. We have tried our
        best to make sure there is no user impact on users. However, there may be regressions with
        new parser backend.

        To revert to the old parser implementation, add `GETGAUGE_USE_0_3_3_PARSER=true` property
        to the `python.properties` file in the `<PROJECT_DIR>/env/default directory.

        This property along with the redbaron parser will be removed in future releases.
        """
        if parser == 'redbaron' or os.environ.get('GETGAUGE_USE_0_3_3_PARSER'):
            PythonFile.Class = RedbaronPythonFile
        else:
            PythonFile.Class = ParsoPythonFile


# Select the default implementation
PythonFile.select_python_parser()


class PythonFileABC(six.with_metaclass(ABCMeta)):
    @staticmethod
    def parse(file_path, content=None):
        """
        Create a PythonFileABC object with specified file_path and content. If content is None
        then, it is loaded from the file_path method. Otherwise, file_path is only used for
        reporting errors.
        """
        raise NotImplementedError

    @abstractmethod
    def iter_steps(self):
        """Iterate over steps in the parsed file"""
        raise NotImplementedError

    @abstractmethod
    def refactor_step(self, old_text, new_text, move_param_from_idx):
        """
        Find the step with old_text and change it to new_text. The step function
        parameters are also changed according to move_param_from_idx. Each entry in
        this list should specify parameter position from old
        """
        raise NotImplementedError

    @abstractmethod
    def get_code(self):
        """Returns current content of the tree."""
        raise NotImplementedError


# Verify that implemetations are subclasses of ABC
PythonFileABC.register(ParsoPythonFile)
PythonFileABC.register(RedbaronPythonFile)
