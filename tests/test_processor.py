from os import path
from textwrap import dedent
from unittest import main

from getgauge import processor
from getgauge import static_loader as loader
from getgauge.messages.messages_pb2 import *
from getgauge.messages.spec_pb2 import Parameter, ProtoExecutionResult, Span
from getgauge.parser import PythonFile
from getgauge.python import data_store
from getgauge.registry import registry
from pyfakefs.fake_filesystem_unittest import TestCase


class ProcessorTests(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        data_store.suite.clear()
        data_store.spec.clear()
        data_store.scenario.clear()
        registry.clear()

    def tearDown(self):
        registry.clear()

    def load_content_steps(self, content):
        content = dedent(content)
        pf = PythonFile.parse("foo.py", content)
        self.assertIsNotNone(pf)
        loader.load_steps(pf)

    def test_Processor_suite_data_store_init_request(self):
        data_store.suite['suite'] = 'value'

        self.assertNotEqual(0, len(data_store.suite))

        response = Message()
        processor.init_suite_data_store(None, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(False,
                         response.executionStatusResponse.executionResult.failed)

        self.assertEqual(0,
                         response.executionStatusResponse.executionResult.executionTime)

        self.assertDictEqual({}, data_store.suite)

    def test_Processor_spec_data_store_init_request(self):
        data_store.spec['spec'] = 'value'

        self.assertNotEqual(0, len(data_store.spec))

        response = Message()
        processor.init_spec_data_store(None, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(
            0, response.executionStatusResponse.executionResult.executionTime)

        self.assertDictEqual({}, data_store.spec)

    def test_Processor_scenario_data_store_init_request(self):
        data_store.scenario['scenario'] = 'value'

        self.assertNotEqual(0, len(data_store.scenario))

        response = Message()
        processor.init_scenario_data_store(None, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(
            0, response.executionStatusResponse.executionResult.executionTime)

        self.assertDictEqual({}, data_store.scenario)

    def test_Processor_step_names_request(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')
        response = Message()

        processor.send_all_step_names(None, response)

        self.assertEqual(Message.StepNamesResponse, response.messageType)
        self.assertEqual({'Step <a> with <b>', 'Step 4'},
                         set(response.stepNamesResponse.steps))

    def test_Processor_step_name_request(self):
        registry.add_step('Step <a> with <b>', 'func', '', {
                          'start': 1, 'startChar': 0, 'end': 3, 'endChar': 10})
        registry.add_step('Step 4', 'func1', '', {
                          'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        response = Message()
        request = StepNameRequest()
        request.stepValue = 'Step {} with {}'

        processor.execute_step_name_request(request, response)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual(['Step <a> with <b>'],
                         response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

        response = Message()
        request = StepNameRequest()
        request.stepValue = 'Step 4'

        processor.execute_step_name_request(request, response)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual(['Step 4'], response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

    def test_Processor_step_name_request_with_aliases(self):
        registry.add_step(['Step 1', 'Step 2', 'Step 3'], 'func1', '',
                          {'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        response = Message()
        request = StepNameRequest()
        request.stepValue = 'Step 1'

        processor.execute_step_name_request(request, response)
        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertTrue('Step 1' in response.stepNameResponse.stepName)
        self.assertTrue('Step 2' in response.stepNameResponse.stepName)
        self.assertTrue('Step 3' in response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(True, response.stepNameResponse.hasAlias)

    def test_Processor_step_name_request_with_unimplemented_step(self):
        response = Message()
        request = StepNameRequest()
        request.stepValue = 'Step {} with {}'

        processor.execute_step_name_request(request, response)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual([], response.stepNameResponse.stepName)
        self.assertEqual(False, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

    def test_Processor_valid_step_validate_request(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        response = Message()

        request = StepValidateRequest()
        request.stepText = 'Step {} with {}'
        processor.validate_step(request, response)

        self.assertEqual(Message.StepValidateResponse, response.messageType)
        self.assertTrue(response.stepValidateResponse.isValid)

    def test_Processor_invalid_step_validate_request_when_no_impl_found(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        response = Message()

        request = StepValidateRequest()
        request.stepText = 'Step2'
        request.stepValue.stepValue = 'Step2'

        processor.validate_step(request, response)

        self.assertEqual(Message.StepValidateResponse, response.messageType)
        self.assertFalse(response.stepValidateResponse.isValid)
        self.assertEqual(StepValidateResponse.STEP_IMPLEMENTATION_NOT_FOUND,
                         response.stepValidateResponse.errorType)
        self.assertTrue('@step("")\ndef step2():\n    assert False, "Add implementation code"' in
                        response.stepValidateResponse.suggestion)

    def test_Processor_invalid_step_validate_request_when_duplicate_impl_found(self):
        registry.add_step('Step <a> with <b>', impl, '', {'start': 0})
        registry.add_step('Step <a> with <b>', impl, '', {'start': 2})

        response = Message()

        request = StepValidateRequest()
        request.stepText = 'Step {} with {}'

        processor.validate_step(request, response)

        self.assertEqual(Message.StepValidateResponse, response.messageType)
        self.assertFalse(response.stepValidateResponse.isValid)
        self.assertEqual(StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION,
                         response.stepValidateResponse.errorType)

    def test_Processor_execute_step_request(self):
        registry.add_step('Step 4', impl1, '')

        response = Message()

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step 4'

        processor.execute_step(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.errorMessage)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_execute_step_request_with_param(self):
        registry.add_step('Step <a> with <b>', impl, '')
        registry.add_step('Step 4', 'func1', '')

        response = Message()

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step {} with {}'
        parameter = Parameter()
        parameter.value = 'param 1'
        parameter1 = Parameter()
        parameter1.value = 'param 2'
        request.parameters.extend([parameter, parameter1])

        processor.execute_step(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.errorMessage)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failed_execute_step_request(self):
        response = Message()
        request = ExecuteStepRequest()

        processor.execute_step(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.recoverableError)

    def test_Processor_failed_execute_step_request_with_continue_on_failure(self):
        registry.add_step('Step 4', failing_impl, '')
        registry.continue_on_failure(failing_impl, [IndexError])

        response = Message()

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step 4'

        processor.execute_step(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.recoverableError)

    def test_Processor_starting_execution_request(self):
        registry.add_before_suite(impl1)
        registry.add_before_suite(impl2)
        response = Message()
        request = ExecutionStartingRequest()
        processor.execute_before_suite_hook(request, response, False)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_ending_execution_request(self):
        registry.add_after_suite(impl1)
        registry.add_after_suite(impl2)
        response = Message()
        request = ExecutionEndingRequest()
        processor.execute_after_suite_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_spec_starting_execution_request(self):
        registry.add_before_spec(impl1)
        registry.add_before_spec(impl2)
        response = Message()
        request = SpecExecutionEndingRequest()
        processor.execute_before_spec_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_spec_ending_execution_request(self):
        registry.add_after_spec(impl1)
        registry.add_after_spec(impl2)
        response = Message()
        request = SpecExecutionEndingRequest()
        processor.execute_after_spec_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_scenario_starting_execution_request(self):
        registry.add_before_scenario(impl1)
        registry.add_before_scenario(impl2)
        response = Message()
        request = ScenarioExecutionStartingRequest()
        processor.execute_before_scenario_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_scenario_ending_execution_request(self):
        registry.add_after_scenario(impl1)
        registry.add_after_scenario(impl2)
        response = Message()
        request = ScenarioExecutionEndingRequest()
        processor.execute_after_scenario_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_step_starting_execution_request(self):
        registry.add_before_step(impl1)
        registry.add_before_step(impl2)
        response = Message()
        request = StepExecutionStartingRequest()
        processor.execute_before_step_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_step_ending_execution_request(self):
        registry.add_after_step(impl1)
        registry.add_after_step(impl2)
        response = Message()
        request = StepExecutionEndingRequest()
        processor.execute_after_step_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_failing_starting_execution_request(self):
        registry.add_before_suite(failing_impl)
        response = Message()
        request = ExecutionStartingRequest()
        processor.execute_before_suite_hook(request, response, False)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_ending_execution_request(self):
        registry.add_after_suite(failing_impl)
        response = Message()
        request = ExecutionEndingRequest()
        processor.execute_after_suite_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_spec_starting_execution_request(self):
        registry.add_before_spec(failing_impl)
        response = Message()
        request = SpecExecutionStartingRequest()
        processor.execute_before_spec_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_spec_ending_execution_request(self):
        registry.add_after_spec(failing_impl)
        response = Message()
        request = SpecExecutionEndingRequest()
        processor.execute_after_spec_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_scenario_starting_execution_request(self):
        registry.add_before_scenario(failing_impl)
        response = Message()
        request = ScenarioExecutionStartingRequest()
        processor.execute_before_scenario_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_scenario_ending_execution_request(self):
        registry.add_after_scenario(failing_impl)
        response = Message()
        request = ScenarioExecutionEndingRequest()
        processor.execute_after_scenario_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_step_starting_execution_request(self):
        registry.add_before_step(failing_impl)
        response = Message()
        request = StepExecutionStartingRequest()
        processor.execute_before_step_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failing_step_ending_execution_request(self):
        registry.add_after_step(failing_impl)
        response = Message()
        request = StepExecutionEndingRequest()
        processor.execute_after_step_hook(request, response)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            True, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionStatusResponse.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionStatusResponse.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_refactor_request_when_multiple_impl_found(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step <a> with <b>', 'func', '')
        response = Message()
        request = RefactorRequest()
        request.oldStepValue.stepValue = 'Step {} with {}'
        request.oldStepValue.parameterizedStepValue = 'Step <a> with <b>'

        processor.refactor(request, response)

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(False, response.refactorResponse.success)
        self.assertEqual('Reason: Multiple Implementation found for `Step <a> with <b>`',
                         response.refactorResponse.error)

    def test_Processor_step_position_request(self):
        registry.add_step('Step <a> with <b>', 'func', 'foo.py',
                          {'start': 0, 'startChar': 0, 'end': 3, 'endChar': 10})
        registry.add_step('Step 1', 'func', 'foo.py', {
                          'start': 4, 'startChar': 0, 'end': 7, 'endChar': 10})

        response = Message()
        request = StepPositionsRequest()
        request.filePath = 'foo.py'

        processor._step_positions(request, response)

        self.assertEqual(Message.StepPositionsResponse, response.messageType)
        self.assertEqual('', response.refactorResponse.error)

        steps = [(p.stepValue, p.span.start)
                 for p in response.stepPositionsResponse.stepPositions]

        self.assertIn(('Step {} with {}', 0), steps)
        self.assertIn(('Step 1', 4), steps)

    def test_Processor_put_stub_impl_request(self):
        request = StubImplementationCodeRequest()
        response = Message()

        codes = ["code1", "code2"]
        request.implementationFilePath = ""
        request.codes.extend(codes)

        processor.get_stub_impl_content(request, response)

        expected_output_codes = dedent('''\
        from getgauge.python import step

        code1
        code2''')
        expected_span = Span(
            **{'start': 0, 'startChar': 0, 'end': 0, 'endChar': 0})
        expected_text_diff = TextDiff(
            **{'span': expected_span, 'content': expected_output_codes})

        self.assertEqual(len(response.fileDiff.textDiffs), 1)
        self.assertEqual(response.fileDiff.textDiffs[0], expected_text_diff)
        self.assertEqual(path.basename(
            response.fileDiff.filePath), "step_implementation.py")

    def test_Processor_glob_pattern(self):
        request = ImplementationFileGlobPatternRequest()
        response = Message()

        processor.glob_pattern(request, response)

        self.assertEqual(response.implementationFileGlobPatternResponse.globPatterns, [
                         "step_impl/**/*.py"])

    def test_Processor_cache_file_with_opened_status(self):
        request = CacheFileRequest()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.filePath = 'foo.py'
        request.content = dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        ''')
        request.status = CacheFileRequest.OPENED

        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_changed_status(self):
        request = CacheFileRequest()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.filePath = 'foo.py'
        request.content = dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        ''')
        request.status = CacheFileRequest.CHANGED

        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_create_status(self):
        request = CacheFileRequest()
        response = Message()

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.CREATED
        self.fs.create_file('foo.py', contents=dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        '''))
        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_create_status_when_file_is_cached(self):
        request = CacheFileRequest()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        ''')

        self.assertEqual(registry.is_implemented('foo {}'), True)

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.CREATED
        self.fs.create_file('foo.py')
        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_closed_status(self):
        request = CacheFileRequest()
        response = Message()

        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.CLOSED
        self.fs.create_file('foo.py', contents=dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        '''))
        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_delete_status(self):
        request = CacheFileRequest()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.DELETED

        processor.cache_file(request, response)

        self.assertEqual(registry.is_implemented('foo1'), False)


def impl(a, b):
    pass


def impl1():
    pass


def impl2(context):
    pass


def failing_impl():
    print([][1])


if __name__ == '__main__':
    main()
