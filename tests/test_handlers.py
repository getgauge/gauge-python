import os
from textwrap import dedent
from unittest import main

from getgauge import static_loader as loader
from getgauge.handlers import RunnerServiceHandler
from getgauge.messages.messages_pb2 import *
from getgauge.messages.spec_pb2 import ProtoStepValue
from getgauge.parser import PythonFile
from getgauge.registry import registry
from getgauge.util import get_step_impl_dirs
from pyfakefs.fake_filesystem_unittest import TestCase


class RunnerServiceHandlerTests(TestCase):
    def setUp(self):
        registry.clear()
        self.setUpPyfakefs()

    def load_content_steps(self, content):
        content = dedent(content)
        pf = PythonFile.parse("foo.py", content)
        self.assertIsNotNone(pf)
        loader.load_steps(pf)

    def test_RunnerServiceHandler_glob_pattern(self):
        handler = RunnerServiceHandler(None)

        req = ImplementationFileGlobPatternRequest()
        res = handler.GetGlobPatterns(req, None)

        self.assertEqual(res.globPatterns, ["step_impl/**/*.py"])

    def test_RunnerServiceHandler_file_list(self):
        handler = RunnerServiceHandler(None)
        req = ImplementationFileListRequest()
        self.fs.create_file(os.path.join(get_step_impl_dirs()[0], 'foo.py'))

        res = handler.GetImplementationFiles(req, None)

        self.assertEqual(os.path.basename(
            res.implementationFilePaths[0]), 'foo.py')

    def test_RunnerServiceHandler_step_names(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps('''\
        @step('foo')
        def foo():
            pass
        ''')

        req = StepNamesRequest()
        res = handler.GetStepNames(req, None)

        self.assertEqual(res.steps, ['foo'])

    def test_RunnerServiceHandler_step_name(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps('''\
        @step('foo')
        def foo():
            pass
        ''')

        req = StepNameRequest(stepValue='foo')
        res = handler.GetStepName(req, None)

        self.assertTrue(res.isStepPresent)
        self.assertEqual(res.fileName, 'foo.py')

    def test_RunnerServiceHandler_validate_step(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps('''\
        @step('foo')
        def foo():
            pass
        ''')
        step_value = ProtoStepValue(
            stepValue='foo', parameterizedStepValue='foo')

        req = StepValidateRequest(
            stepText='foo', stepValue=step_value, numberOfParameters=0)
        res = handler.ValidateStep(req, None)
        self.assertTrue(res.isValid)

    def test_RunnerServiceHandler_step_positions(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps('''\
        @step('foo')
        def foo():
            pass
        ''')

        req = StepPositionsRequest(filePath='foo.py')
        res = handler.GetStepPositions(req, None)
        self.assertEqual(res.stepPositions[0].stepValue, 'foo')

    def test_RunnerServiceHandler_implement_stub(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps("@step('foo')\ndef foo():\n\tpass\n")

        req = StubImplementationCodeRequest(
            implementationFilePath='New File', codes=['add hello'])
        res = handler.ImplementStub(req, None)
        self.assertEqual(os.path.basename(res.filePath),
                         'step_implementation.py')
        self.assertEqual(
            res.textDiffs[0].content, 'from getgauge.python import step\n\nadd hello')

    def test_RunnerServiceHandler_refactor(self):
        handler = RunnerServiceHandler(None)
        content = dedent('''\
        from getgauge.python import step

        @step('Vowels in English language are <aeiou>.')
        def foo(vowels):
            print(vowels)
        ''')
        self.fs.create_file(os.path.join(
            get_step_impl_dirs()[0], 'foo.py'), contents=content)
        loader.load_files(get_step_impl_dirs())

        request = RefactorRequest()
        request.saveChanges = False
        request.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.oldStepValue.parameters.append('vowels')
        request.newStepValue.parameterizedStepValue = 'Vowels in English language is <vowels> <bsdfdsf>.'
        request.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.newStepValue.parameters.extend(['vowels', 'bsdfdsf'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.paramPositions.extend([position, param_position])

        res = handler.Refactor(request, None, False)

        self.assertTrue(res.success)
        diff_contents = [diff.content for diff in res.fileChanges[0].diffs]
        self.assertIn("vowels, arg1", diff_contents)
        self.assertIn(
            "'Vowels in English language is <vowels> <bsdfdsf>.'", diff_contents)

    def test_RunnerServiceHandler_cache_file(self):
        handler = RunnerServiceHandler(None)
        self.load_content_steps('''\
        from getgauge.python import step

        @step('Vowels in English language are <aeiou>.')
        def foo(vowels):
            print(vowels)
        ''')

        self.assertTrue(registry.is_implemented(
            'Vowels in English language are {}.'))

        content = dedent('''\
        from getgauge.python import step

        @step('get lost!')
        def foo():
            pass
        ''')
        req = CacheFileRequest(
            content=content, filePath='foo.py', status=CacheFileRequest.CHANGED)
        handler.CacheFile(req, None)

        self.assertTrue(registry.is_implemented('get lost!'))


if __name__ == '__main__':
    main()
