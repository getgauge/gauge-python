from os import path
from socket import socket, AF_INET, SOCK_STREAM
from unittest import main
from textwrap import dedent
from pyfakefs.fake_filesystem_unittest import TestCase
from getgauge import static_loader as loader
from getgauge.messages.messages_pb2 import Message, StepValidateResponse, TextDiff, CacheFileRequest
from getgauge.messages.spec_pb2 import ProtoExecutionResult, Parameter, Span
from getgauge.processor import processors
from getgauge.python import data_store
from getgauge.registry import registry
from getgauge.parser import PythonFile


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

    def test_Processor_kill_request(self):
        with self.assertRaises(SystemExit):
            processors[Message.KillProcessRequest](None,
                                                   None,
                                                   socket(AF_INET,
                                                          SOCK_STREAM))

    def test_Processor_suite_data_store_init_request(self):
        data_store.suite['suite'] = 'value'

        self.assertNotEqual(0, len(data_store.suite))

        response = Message()
        processors[Message.SuiteDataStoreInit](None, response, None)

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
        processors[Message.SpecDataStoreInit](None, response, None)

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
        processors[Message.ScenarioDataStoreInit](None, response, None)

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

        processors[Message.StepNamesRequest](None, response, None)

        self.assertEqual(Message.StepNamesResponse, response.messageType)
        self.assertEqual({'Step <a> with <b>', 'Step 4'},
                         set(response.stepNamesResponse.steps))

    def test_Processor_step_name_request(self):
        registry.add_step('Step <a> with <b>', 'func', '', {
                          'start': 1, 'startChar': 0, 'end': 3, 'endChar': 10})
        registry.add_step('Step 4', 'func1', '', {
                          'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        response = Message()
        request = Message()
        request.stepNameRequest.stepValue = 'Step {} with {}'

        processors[Message.StepNameRequest](request, response, None)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual(['Step <a> with <b>'],
                         response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

        response = Message()
        request = Message()
        request.stepNameRequest.stepValue = 'Step 4'

        processors[Message.StepNameRequest](request, response, None)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual(['Step 4'], response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

    def test_Processor_step_name_request_with_aliases(self):
        registry.add_step(['Step 1', 'Step 2', 'Step 3'], 'func1', '',
                          {'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        response = Message()
        request = Message()
        request.stepNameRequest.stepValue = 'Step 1'

        processors[Message.StepNameRequest](request, response, None)
        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertTrue('Step 1' in response.stepNameResponse.stepName)
        self.assertTrue('Step 2' in response.stepNameResponse.stepName)
        self.assertTrue('Step 3' in response.stepNameResponse.stepName)
        self.assertEqual(True, response.stepNameResponse.isStepPresent)
        self.assertEqual(True, response.stepNameResponse.hasAlias)

    def test_Processor_step_name_request_with_unimplemented_step(self):
        response = Message()
        request = Message()
        request.stepNameRequest.stepValue = 'Step {} with {}'

        processors[Message.StepNameRequest](request, response, None)

        self.assertEqual(Message.StepNameResponse, response.messageType)
        self.assertEqual([], response.stepNameResponse.stepName)
        self.assertEqual(False, response.stepNameResponse.isStepPresent)
        self.assertEqual(False, response.stepNameResponse.hasAlias)

    def test_Processor_valid_step_validate_request(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        response = Message()

        request = Message()
        request.stepValidateRequest.stepText = 'Step {} with {}'

        processors[Message.StepValidateRequest](request, response, None)

        self.assertEqual(Message.StepValidateResponse, response.messageType)
        self.assertTrue(response.stepValidateResponse.isValid)

    def test_Processor_invalid_step_validate_request_when_no_impl_found(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        response = Message()

        request = Message()
        request.stepValidateRequest.stepText = 'Step2'
        request.stepValidateRequest.stepValue.stepValue = 'Step2'

        processors[Message.StepValidateRequest](request, response, None)

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

        request = Message()
        request.stepValidateRequest.stepText = 'Step {} with {}'

        processors[Message.StepValidateRequest](request, response, None)

        self.assertEqual(Message.StepValidateResponse, response.messageType)
        self.assertFalse(response.stepValidateResponse.isValid)
        self.assertEqual(StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION,
                         response.stepValidateResponse.errorType)

    def test_Processor_execute_step_request(self):
        registry.add_step('Step 4', impl1, '')

        response = Message()

        request = Message()
        request.executeStepRequest.parsedStepText = 'Step 4'

        processors[Message.ExecuteStep](request, response, None)

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

        request = Message()
        request.executeStepRequest.parsedStepText = 'Step {} with {}'
        parameter = Parameter()
        parameter.value = 'param 1'
        parameter1 = Parameter()
        parameter1.value = 'param 2'
        request.executeStepRequest.parameters.extend([parameter, parameter1])

        processors[Message.ExecuteStep](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.errorMessage)
        self.assertEqual(
            '', response.executionStatusResponse.executionResult.stackTrace)

    def test_Processor_failed_execute_step_request(self):
        response = Message()
        request = Message()

        processors[Message.ExecuteStep](request, response, None)

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

        request = Message()
        request.executeStepRequest.parsedStepText = 'Step 4'

        processors[Message.ExecuteStep](request, response, None)

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
        request = Message()
        processors[Message.ExecutionStarting](request, response, None, False)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_ending_execution_request(self):
        registry.add_after_suite(impl1)
        registry.add_after_suite(impl2)
        response = Message()
        request = Message()
        processors[Message.ExecutionEnding](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_spec_starting_execution_request(self):
        registry.add_before_spec(impl1)
        registry.add_before_spec(impl2)
        response = Message()
        request = Message()
        processors[Message.SpecExecutionStarting](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_spec_ending_execution_request(self):
        registry.add_after_spec(impl1)
        registry.add_after_spec(impl2)
        response = Message()
        request = Message()
        processors[Message.SpecExecutionEnding](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_scenario_starting_execution_request(self):
        registry.add_before_scenario(impl1)
        registry.add_before_scenario(impl2)
        response = Message()
        request = Message()
        processors[Message.ScenarioExecutionStarting](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_scenario_ending_execution_request(self):
        registry.add_after_scenario(impl1)
        registry.add_after_scenario(impl2)
        response = Message()
        request = Message()
        processors[Message.ScenarioExecutionEnding](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_step_starting_execution_request(self):
        registry.add_before_step(impl1)
        registry.add_before_step(impl2)
        response = Message()
        request = Message()
        processors[Message.StepExecutionStarting](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_step_ending_execution_request(self):
        registry.add_after_step(impl1)
        registry.add_after_step(impl2)
        response = Message()
        request = Message()
        processors[Message.StepExecutionEnding](request, response, None)

        self.assertEqual(Message.ExecutionStatusResponse, response.messageType)
        self.assertEqual(
            False, response.executionStatusResponse.executionResult.failed)

    def test_Processor_failing_starting_execution_request(self):
        registry.add_before_suite(failing_impl)
        response = Message()
        request = Message()
        processors[Message.ExecutionStarting](request, response, None, False)

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
        request = Message()
        processors[Message.ExecutionEnding](request, response, None)

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
        request = Message()
        processors[Message.SpecExecutionStarting](request, response, None)

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
        request = Message()
        processors[Message.SpecExecutionEnding](request, response, None)

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
        request = Message()
        processors[Message.ScenarioExecutionStarting](request, response, None)

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
        request = Message()
        processors[Message.ScenarioExecutionEnding](request, response, None)

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
        request = Message()
        processors[Message.StepExecutionStarting](request, response, None)

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
        request = Message()
        processors[Message.StepExecutionEnding](request, response, None)

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
        request = Message()
        request.refactorRequest.oldStepValue.stepValue = 'Step {} with {}'
        request.refactorRequest.oldStepValue.parameterizedStepValue = 'Step <a> with <b>'

        processors[Message.RefactorRequest](request, response, None)

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
        request = Message()
        request.stepPositionsRequest.filePath = 'foo.py'

        processors[Message.StepPositionsRequest](request, response, None)

        self.assertEqual(Message.StepPositionsResponse, response.messageType)
        self.assertEqual('', response.refactorResponse.error)

        steps = [(p.stepValue, p.span.start)
                 for p in response.stepPositionsResponse.stepPositions]

        self.assertIn(('Step {} with {}', 0), steps)
        self.assertIn(('Step 1', 4), steps)

    def test_Processor_put_stub_impl_request(self):
        request = Message()
        response = Message()

        codes = ["code1", "code2"]
        request.stubImplementationCodeRequest.implementationFilePath = ""
        request.stubImplementationCodeRequest.codes.extend(codes)

        processors[Message.StubImplementationCodeRequest](
            request, response, None)

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
        request = Message()
        response = Message()

        processors[Message.ImplementationFileGlobPatternRequest](
            request, response, None)

        self.assertEqual(response.implementationFileGlobPatternResponse.globPatterns, [
                         "step_impl/**/*.py"])

    def test_Processor_cache_file_with_opened_status(self):
        request = Message()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.cacheFileRequest.filePath = 'foo.py'
        request.cacheFileRequest.content = dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        ''')
        request.cacheFileRequest.status = CacheFileRequest.OPENED

        processors[Message.CacheFileRequest](request, response, None)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_changed_status(self):
        request = Message()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.cacheFileRequest.filePath = 'foo.py'
        request.cacheFileRequest.content = dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        ''')
        request.cacheFileRequest.status = CacheFileRequest.CHANGED

        processors[Message.CacheFileRequest](request, response, None)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_create_status(self):
        request = Message()
        response = Message()

        request.cacheFileRequest.filePath = 'foo.py'
        request.cacheFileRequest.status = CacheFileRequest.CREATED
        self.fs.create_file('foo.py', contents=dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        '''))
        processors[Message.CacheFileRequest](request, response, None)

        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_closed_status(self):
        request = Message()
        response = Message()

        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.cacheFileRequest.filePath = 'foo.py'
        request.cacheFileRequest.status = CacheFileRequest.CLOSED
        self.fs.create_file('foo.py', contents=dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        '''))
        processors[Message.CacheFileRequest](request, response, None)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_delete_status(self):
        request = Message()
        response = Message()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.cacheFileRequest.filePath = 'foo.py'
        request.cacheFileRequest.status = CacheFileRequest.DELETED

        processors[Message.CacheFileRequest](request, response, None)

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
