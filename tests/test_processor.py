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

        response = processor.process_suite_data_store_init_request()

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)
        self.assertEqual(0, response.executionResult.executionTime)
        self.assertDictEqual({}, data_store.suite)

    def test_Processor_spec_data_store_init_request(self):
        data_store.spec['spec'] = 'value'

        self.assertNotEqual(0, len(data_store.spec))

        response = processor.process_spec_data_store_init_request()

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)
        self.assertEqual(0, response.executionResult.executionTime)
        self.assertDictEqual({}, data_store.spec)

    def test_Processor_scenario_data_store_init_request(self):
        data_store.scenario['scenario'] = 'value'

        self.assertNotEqual(0, len(data_store.scenario))

        response = processor.process_scenario_data_store_init_request()

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)
        self.assertEqual(0, response.executionResult.executionTime)
        self.assertDictEqual({}, data_store.scenario)

    def test_Processor_step_names_request(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        response = processor.process_step_names_request()

        self.assertTrue(isinstance(response, StepNamesResponse))
        self.assertEqual({'Step <a> with <b>', 'Step 4'}, set(response.steps))

    def test_Processor_step_name_request(self):
        registry.add_step('Step <a> with <b>', 'func', '', {
                          'start': 1, 'startChar': 0, 'end': 3, 'endChar': 10})
        registry.add_step('Step 4', 'func1', '', {
                          'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        request = StepNameRequest()
        request.stepValue = 'Step {} with {}'

        response = processor.process_step_name_request(request)
        self.assertTrue(isinstance(response, StepNameResponse))
        self.assertEqual(['Step <a> with <b>'], response.stepName)
        self.assertEqual(True, response.isStepPresent)
        request = StepNameRequest()
        self.assertEqual(False, response.hasAlias)

        request.stepValue = 'Step 4'
        response = processor.process_step_name_request(request)

        self.assertTrue(isinstance(response, StepNameResponse))
        self.assertEqual(['Step 4'], response.stepName)
        self.assertEqual(True, response.isStepPresent)
        self.assertEqual(False, response.hasAlias)

    def test_Processor_step_name_request_with_aliases(self):
        registry.add_step(['Step 1', 'Step 2', 'Step 3'], 'func1', '',
                          {'start': 5, 'startChar': 0, 'end': 6, 'endChar': 10})
        request = StepNameRequest()
        request.stepValue = 'Step 1'

        response = processor.process_step_name_request(request)

        self.assertTrue(isinstance(response, StepNameResponse))
        self.assertTrue('Step 1' in response.stepName)
        self.assertTrue('Step 2' in response.stepName)
        self.assertTrue('Step 3' in response.stepName)
        self.assertEqual(True, response.isStepPresent)
        self.assertEqual(True, response.hasAlias)

    def test_Processor_step_name_request_with_unimplemented_step(self):
        request = StepNameRequest()
        request.stepValue = 'Step {} with {}'

        response = processor.process_step_name_request(request)

        self.assertTrue(isinstance(response, StepNameResponse))
        self.assertEqual([], response.stepName)
        self.assertEqual(False, response.isStepPresent)
        self.assertEqual(False, response.hasAlias)

    def test_Processor_valid_step_validate_request(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        request = StepValidateRequest()
        request.stepText = 'Step {} with {}'
        response = processor.process_validate_step_request(request)

        self.assertTrue(isinstance(response, StepValidateResponse))
        self.assertTrue(response.isValid)

    def test_Processor_invalid_step_validate_request_when_no_impl_found(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step 4', 'func1', '')

        request = StepValidateRequest()
        request.stepText = 'Step2'
        request.stepValue.stepValue = 'Step2'

        response = processor.process_validate_step_request(request)

        self.assertTrue(isinstance(response, StepValidateResponse))
        self.assertFalse(response.isValid)
        self.assertEqual(StepValidateResponse.STEP_IMPLEMENTATION_NOT_FOUND,
                         response.errorType)
        self.assertTrue('@step("")\ndef step2():\n    assert False, "Add implementation code"' in
                        response.suggestion)

    def test_Processor_invalid_step_validate_request_when_duplicate_impl_found(self):
        registry.add_step('Step <a> with <b>', impl, '', {'start': 0})
        registry.add_step('Step <a> with <b>', impl, '', {'start': 2})

        response = Message()

        request = StepValidateRequest()
        request.stepText = 'Step {} with {}'

        response = processor.process_validate_step_request(request)

        self.assertTrue(isinstance(response, StepValidateResponse))
        self.assertFalse(response.isValid)
        self.assertEqual(StepValidateResponse.DUPLICATE_STEP_IMPLEMENTATION,
                         response.errorType)

    def test_Processor_execute_step_request(self):
        registry.add_step('Step 4', impl1, '')

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step 4'

        response = processor.process_execute_step_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            False, response.executionResult.failed)
        self.assertEqual(
            '', response.executionResult.errorMessage)
        self.assertEqual(
            '', response.executionResult.stackTrace)

    def test_Processor_execute_step_request_with_param(self):
        registry.add_step('Step <a> with <b>', impl, '')
        registry.add_step('Step 4', 'func1', '')

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step {} with {}'
        parameter = Parameter()
        parameter.value = 'param 1'
        parameter1 = Parameter()
        parameter1.value = 'param 2'
        request.parameters.extend([parameter, parameter1])

        response = processor.process_execute_step_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            False, response.executionResult.failed)
        self.assertEqual(
            '', response.executionResult.errorMessage)
        self.assertEqual(
            '', response.executionResult.stackTrace)

    def test_Processor_failed_execute_step_request(self):
        request = ExecuteStepRequest()

        response = processor.process_execute_step_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertNotEqual(
            '', response.executionResult.errorMessage)
        self.assertNotEqual(
            '', response.executionResult.stackTrace)
        self.assertEqual(
            False, response.executionResult.recoverableError)

    def test_Processor_failed_execute_step_request_with_continue_on_failure(self):
        registry.add_step('Step 4', failing_impl, '')
        registry.continue_on_failure(failing_impl, [IndexError])

        request = ExecuteStepRequest()
        request.parsedStepText = 'Step 4'

        response = processor.process_execute_step_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertNotEqual('', response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)
        self.assertEqual(True, response.executionResult.recoverableError)

    def test_Processor_starting_execution_request(self):
        registry.add_before_suite(impl1)
        registry.add_before_suite(impl2)
        request = ExecutionStartingRequest()
        response = processor.process_execution_starting_reqeust(request, False)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_ending_execution_request(self):
        registry.add_after_suite(impl1)
        registry.add_after_suite(impl2)
        request = ExecutionEndingRequest()
        response = processor.process_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_spec_starting_execution_request(self):
        registry.add_before_spec(impl1)
        registry.add_before_spec(impl2)
        request = SpecExecutionEndingRequest()
        response = processor.process_spec_execution_starting_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_spec_ending_execution_request(self):
        registry.add_after_spec(impl1)
        registry.add_after_spec(impl2)
        request = SpecExecutionEndingRequest()
        response = processor.process_spec_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_scenario_starting_execution_request(self):
        registry.add_before_scenario(impl1)
        registry.add_before_scenario(impl2)
        request = ScenarioExecutionStartingRequest()
        response = processor.process_scenario_execution_starting_request(
            request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_scenario_ending_execution_request(self):
        registry.add_after_scenario(impl1)
        registry.add_after_scenario(impl2)
        request = ScenarioExecutionEndingRequest()
        response = processor.process_scenario_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_step_starting_execution_request(self):
        registry.add_before_step(impl1)
        registry.add_before_step(impl2)
        request = StepExecutionStartingRequest()
        response = processor.process_step_execution_starting_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_step_ending_execution_request(self):
        registry.add_after_step(impl1)
        registry.add_after_step(impl2)
        request = StepExecutionEndingRequest()
        response = processor.process_step_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(False, response.executionResult.failed)

    def test_Processor_failing_starting_execution_request(self):
        registry.add_before_suite(failing_impl)
        request = ExecutionStartingRequest()
        response = processor.process_execution_starting_reqeust(
            request, False)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_ending_execution_request(self):
        registry.add_after_suite(failing_impl)
        request = ExecutionEndingRequest()
        response = processor.process_execution_ending_request(request)
        print(response)
        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_spec_starting_execution_request(self):
        registry.add_before_spec(failing_impl)
        request = SpecExecutionStartingRequest()
        response = processor.process_spec_execution_starting_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_spec_ending_execution_request(self):
        registry.add_after_spec(failing_impl)
        request = SpecExecutionEndingRequest()
        response = processor.process_spec_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_scenario_starting_execution_request(self):
        registry.add_before_scenario(failing_impl)
        request = ScenarioExecutionStartingRequest()
        response = processor.process_scenario_execution_starting_request(
            request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_scenario_ending_execution_request(self):
        registry.add_after_scenario(failing_impl)
        request = ScenarioExecutionEndingRequest()
        response = processor.process_scenario_execution_ending_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_step_starting_execution_request(self):
        registry.add_before_step(failing_impl)
        request = StepExecutionStartingRequest()
        response = processor.process_step_execution_starting_request(request)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_failing_step_ending_execution_request(self):
        registry.add_after_step(failing_impl)
        request = StepExecutionEndingRequest()
        response = processor.process_step_execution_ending_request(request,)

        self.assertTrue(isinstance(response, ExecutionStatusResponse))
        self.assertEqual(
            True, response.executionResult.failed)
        self.assertEqual(ProtoExecutionResult.ASSERTION,
                         response.executionResult.errorType)
        self.assertEqual('list index out of range',
                         response.executionResult.errorMessage)
        self.assertNotEqual('', response.executionResult.stackTrace)

    def test_Processor_refactor_request_when_multiple_impl_found(self):
        registry.add_step('Step <a> with <b>', 'func', '')
        registry.add_step('Step <a> with <b>', 'func', '')
        request = RefactorRequest()
        request.oldStepValue.stepValue = 'Step {} with {}'
        request.oldStepValue.parameterizedStepValue = 'Step <a> with <b>'

        response = processor.process_refactor_request(request)

        self.assertTrue(isinstance(response, RefactorResponse))
        self.assertEqual(False, response.success)
        self.assertEqual(
            'Reason: Multiple Implementation found for `Step <a> with <b>`', response.error)

    def test_Processor_step_position_request(self):

        registry.add_step('Step <a> with <b>', 'func', 'foo.py',
                          {'start': 0, 'startChar': 0, 'end': 3, 'endChar': 10})
        registry.add_step('Step 1', 'func', 'foo.py', {
                          'start': 4, 'startChar': 0, 'end': 7, 'endChar': 10})

        request = StepPositionsRequest()
        request.filePath = 'foo.py'

        response = processor.prceoss_step_positions_request(request)

        self.assertTrue(isinstance(response, StepPositionsResponse))
        self.assertEqual('', response.error)

        steps = [(p.stepValue, p.span.start)
                 for p in response.stepPositions]

        self.assertIn(('Step {} with {}', 0), steps)
        self.assertIn(('Step 1', 4), steps)

    def test_Processor_put_stub_impl_request(self):
        request = StubImplementationCodeRequest()

        codes = ["code1", "code2"]
        request.implementationFilePath = ""
        request.codes.extend(codes)

        response = processor.process_stub_impl_request(request)

        expected_output_codes = dedent('''\
        from getgauge.python import step

        code1
        code2''')
        expected_span = Span(
            **{'start': 0, 'startChar': 0, 'end': 0, 'endChar': 0})
        expected_text_diff = TextDiff(
            **{'span': expected_span, 'content': expected_output_codes})

        self.assertEqual(len(response.textDiffs), 1)
        self.assertEqual(response.textDiffs[0], expected_text_diff)
        self.assertEqual(path.basename(
            response.filePath), "step_implementation.py")

    def test_Processor_glob_pattern(self):
        request = ImplementationFileGlobPatternRequest()
        response = processor.process_glob_pattern_request(request)

        self.assertEqual(response.globPatterns, ["step_impl/**/*.py"])

    def test_Processor_cache_file_with_opened_status(self):
        request = CacheFileRequest()
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

        processor.process_cache_file_request(request)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_changed_status(self):
        request = CacheFileRequest()
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

        processor.process_cache_file_request(request)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_create_status(self):
        request = CacheFileRequest()

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.CREATED
        self.fs.create_file('foo.py', contents=dedent('''\
        from getgauge.python import step

        @step('foo <bar>')
        def foo():
            pass
        '''))
        processor.process_cache_file_request(request)

        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_create_status_when_file_is_cached(self):
        request = CacheFileRequest()
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
        processor.process_cache_file_request(request)

        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_closed_status(self):
        request = CacheFileRequest()

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
        processor.process_cache_file_request(request)

        self.assertEqual(registry.is_implemented('foo1'), False)
        self.assertEqual(registry.is_implemented('foo {}'), True)

    def test_Processor_cache_file_with_delete_status(self):
        request = CacheFileRequest()
        self.load_content_steps('''\
        from getgauge.python import step

        @step('foo1')
        def foo():
            pass
        ''')

        request.filePath = 'foo.py'
        request.status = CacheFileRequest.DELETED

        processor.process_cache_file_request(request)

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
