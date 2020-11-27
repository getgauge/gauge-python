from unittest import TestCase, main

from getgauge.messages.messages_pb2 import Message
from getgauge.registry import registry, MessagesStore, ScreenshotsStore
from getgauge.python import (Messages, DataStore, DictObject,
                             DataStoreContainer, data_store, Table, Specification,
                             Scenario, Step, ExecutionContext,
                             create_execution_context_from)
from uuid import uuid1
import os
import tempfile
try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

registry.clear()


class MessagesTests(TestCase):
    def test_pending_messages(self):
        messages = ['HAHAHAH', 'HAHAHAH1', 'HAHAHAH2', 'HAHAHAH3']
        for message in messages:
            Messages.write_message(message)
        pending_messages = MessagesStore.pending_messages()
        self.assertEqual(messages, pending_messages)

    def test_clear(self):
        messages = ['HAHAHAH', 'HAHAHAH1', 'HAHAHAH2', 'HAHAHAH3']
        for message in messages:
            Messages.write_message(message)
        MessagesStore.clear()
        pending_messages = MessagesStore.pending_messages()
        self.assertEqual([], pending_messages)

    def test_pending_messages_gives_only_those_messages_which_are_not_reported(self):
        messages = ['HAHAHAH', 'HAHAHAH1', 'HAHAHAH2', 'HAHAHAH3']
        for message in messages:
            Messages.write_message(message)
        pending_messages = MessagesStore.pending_messages()
        self.assertEqual(messages, pending_messages)

        pending_messages = MessagesStore.pending_messages()

        self.assertEqual([], pending_messages)

        messages = ['HAHAHAH', 'HAHAHAH1']
        for message in messages:
            Messages.write_message(message)

        pending_messages = MessagesStore.pending_messages()

        self.assertEqual(messages, pending_messages)


class DataStoreTests(TestCase):
    def test_data_store(self):
        store = DataStore()
        values = {'key': 'HAHAHAH',
                  'key1': 'HAHAHAH1',
                  'key2': 'HAHAHAH2',
                  'key3': 'HAHAHAH3'}

        for value in values:
            store.put(value, value)

        for value in values:
            store.put(value, values[value])

        for value in values:
            self.assertEqual(store.get(value), values[value])

    def test_data_store_clear(self):
        store = DataStore()
        values = {'key': 'HAHAHAH',
                  'key1': 'HAHAHAH1',
                  'key2': 'HAHAHAH2',
                  'key3': 'HAHAHAH3'}

        for value in values:
            store.put(value, value)

        for value in values:
            store.put(value, values[value])

        for value in values:
            self.assertTrue(store.is_present(value))

        store.clear()

        for value in values:
            self.assertFalse(store.is_present(value))

    def test_data_store_equality(self):
        store = DataStore()
        store1 = DataStore()

        self.assertEqual(store, store1)

        store.put('a', 'b')
        store1.put('a', 'b')

        self.assertEqual(store, store1)

        store.put('b', 'b')
        store1.put('c', 'b')

        self.assertNotEqual(store, store1)

    def test_data_store_as_proxy(self):
        store = {}
        proxy = DataStore(store)

        store['a'] = 'alpha'
        self.assertTrue(proxy.is_present('a'))
        self.assertEqual(proxy.get('a'), store['a'])

        proxy.put('b', 'beta')
        self.assertIn('b', store)
        self.assertEqual(store['b'], proxy.get('b'))

        proxy2 = DataStore(store)
        self.assertEqual(proxy, proxy2)

        proxy.clear()
        self.assertDictEqual(store, {})
        self.assertFalse(proxy2.is_present('a'))
        self.assertFalse(proxy2.is_present('b'))

        proxy2.put('c', 'charlie')
        proxy2.put('d', 'delta')
        self.assertIn('c', store)
        self.assertIn('d', store)
        self.assertTrue(proxy.is_present('c'))
        self.assertTrue(proxy.is_present('d'))

        store.clear()
        self.assertFalse(proxy.is_present('c'))
        self.assertFalse(proxy.is_present('d'))
        self.assertFalse(proxy2.is_present('c'))
        self.assertFalse(proxy2.is_present('d'))

class DictObjectTests(TestCase):
    def test_attribute_access(self):
        store = DictObject()

        store['a'] = 'alpha'
        self.assertEqual(store.a, 'alpha')

        store.clear()
        with self.assertRaises(AttributeError):
            store.a

        store.b = 'beta'
        self.assertIn('b', store)
        del store.b
        self.assertNotIn('b', store)

        store['k e y'] = 'value'
        with self.assertRaises(AttributeError):
            store.k


class DataStoreContainerTests(TestCase):
    def test_data_store_container(self):
        store = DataStoreContainer()
        # Verify that each store is a mapping
        self.assertIsInstance(store.scenario, MutableMapping)
        self.assertIsInstance(store.spec, MutableMapping)
        self.assertIsInstance(store.suite, MutableMapping)
        # Verify that stores can not be reassigned
        with self.assertRaises(AttributeError):
            store.scenario = {}
        with self.assertRaises(AttributeError):
            store.spec = {}
        with self.assertRaises(AttributeError):
            store.suite = {}

    def test_module_data_store(self):
        self.assertIsInstance(data_store, DataStoreContainer)


class ProtoTable:
    def __init__(self, table_dict):
        self.headers = ProtoRow(table_dict['headers']['cells'])
        self.rows = [ProtoRow(row['cells']) for row in table_dict['rows']]


class ProtoRow:
    def __init__(self, cells):
        self.cells = cells


class TableTests(TestCase):
    def test_Table(self):
        headers = ['Product', 'Description']
        rows = [{'cells': ['Gauge', 'Test automation with ease']},
                {'cells': ['Mingle', 'Agile project management']},
                {'cells': ['Snap', 'Hosted continuous integration']},
                {'cells': ['Gocd', 'Continuous delivery platform']}]

        proto_table = ProtoTable({'headers': {'cells': headers}, 'rows': rows})

        table = Table(proto_table)

        expected_rows = [row['cells'] for row in rows]
        expected_column_1 = [row['cells'][0] for row in rows]
        expected_column_2 = [row['cells'][1] for row in rows]

        self.assertEqual(headers, table.headers)
        self.assertEqual(expected_rows, table.rows)
        self.assertEqual(expected_column_1,
                         table.get_column_values_with_index(1))
        self.assertEqual(expected_column_2,
                         table.get_column_values_with_index(2))
        self.assertEqual(expected_column_1,
                         table.get_column_values_with_name(headers[0]))
        self.assertEqual(expected_column_2,
                         table.get_column_values_with_name(headers[1]))

        for row in expected_rows:
            self.assertEqual(row, table.get_row(expected_rows.index(row) + 1))

        with self.assertRaises(IndexError):
            table.get_row(5)

    def test_Table_with_index_access(self):
        headers = ['Product', 'Description']
        rows = [{'cells': ['Gauge', 'Test automation with ease']},
                {'cells': ['Mingle', 'Agile project management']},
                {'cells': ['Snap', 'Hosted continuous integration']},
                {'cells': ['Gocd', 'Continuous delivery platform']}]

        proto_table = ProtoTable({'headers': {'cells': headers}, 'rows': rows})

        table = Table(proto_table)

        expected_rows = [row['cells'] for row in rows]

        for row in expected_rows:
            self.assertEqual(row, table[expected_rows.index(row)])

        for row in table:
            self.assertTrue(expected_rows.__contains__(row))

        with self.assertRaises(IndexError):
            table.get_row(5)

    def test_Table_equality(self):
        headers = ['Product', 'Description']
        rows = [{'cells': ['Gauge', 'Test automation with ease']},
                {'cells': ['Mingle', 'Agile project management']},
                {'cells': ['Snap', 'Hosted continuous integration']},
                {'cells': ['Gocd', 'Continuous delivery platform']}]

        proto_table = ProtoTable({'headers': {'cells': headers}, 'rows': rows})

        table = Table(proto_table)
        table1 = Table(proto_table)

        self.assertEqual(table, table1)

    def test_Table__str__(self):
        headers = ['Word', 'Vowel Count']
        rows = [{'cells': ['Gauge', '3']},
                {'cells': ['Mingle', '2']},
                {'cells': ['Snap', '1']},
                {'cells': ['GoCD', '1']},
                {'cells': ['Rhythm', '0']}]

        proto_table = ProtoTable({'headers': {'cells': headers}, 'rows': rows})

        table = Table(proto_table).__str__()

        self.assertEqual(table, """|Word  |Vowel Count|
|------|-----------|
|Gauge |3          |
|Mingle|2          |
|Snap  |1          |
|GoCD  |1          |
|Rhythm|0          |""")

    def test_Table__str__without_rows(self):
        headers = ['Word', 'Vowel Count']
        rows = []

        proto_table = ProtoTable({'headers': {'cells': headers}, 'rows': rows})

        table = Table(proto_table).__str__()

        self.assertEqual(table, """|Word|Vowel Count|
|----|-----------|""")


class SpecificationTests(TestCase):
    def test_Specification(self):
        name = 'NAME'
        file_name = 'FILE_NAME'
        tags = ['TAGS']
        specification = Specification(name, file_name, False, tags)

        self.assertEqual(specification.name, name)
        self.assertEqual(specification.file_name, file_name)
        self.assertEqual(specification.is_failing, False)
        self.assertEqual(specification.tags, tags)

    def test_Specification_equality(self):
        name = 'NAME'
        file_name = 'FILE_NAME'
        tags = ['TAGS']
        specification = Specification(name, file_name, False, tags)
        specification1 = Specification(name, file_name, False, tags)

        self.assertEqual(specification, specification1)


class ScenarioTests(TestCase):
    def test_Scenario(self):
        name = 'NAME3'
        tags = ['TAGS']
        scenario = Scenario(name, False, tags)

        self.assertEqual(scenario.name, name)
        self.assertEqual(scenario.is_failing, False)
        self.assertEqual(scenario.tags, tags)

    def test_Scenario_equality(self):
        name = 'NAME2'
        tags = ['TAGS']
        scenario = Scenario(name, False, tags)
        scenario1 = Scenario(name, False, tags)

        self.assertEqual(scenario, scenario1)


class StepTests(TestCase):
    def test_Step(self):
        name = 'NAME1'
        step = Step(name, False)

        self.assertEqual(step.text, name)
        self.assertEqual(step.is_failing, False)

    def test_Step_equality(self):
        name = 'NAME1'
        step = Step(name, False)
        step1 = Step(name, False)

        self.assertEqual(step, step1)


class ExecutionContextTests(TestCase):
    def test_ExecutionContextTests(self):
        name = 'NAME'
        file_name = 'FILE_NAME'
        tags = ['TAGS']
        specification = Specification(name, file_name, False, tags)
        scenario = Scenario(name, False, tags)
        step = Step(name, False)

        context = ExecutionContext(specification, scenario, step)
        self.assertEqual(specification, context.specification)
        self.assertEqual(scenario, context.scenario)
        self.assertEqual(step, context.step)

    def test_ExecutionContextTests_equality(self):
        name = 'NAME'
        file_name = 'FILE_NAME'
        tags = ['TAGS']
        specification = Specification(name, file_name, False, tags)
        scenario = Scenario(name, False, tags)
        step = Step(name, False)

        context = ExecutionContext(specification, scenario, step)
        context1 = ExecutionContext(specification, scenario, step)

        self.assertEqual(context, context1)

    def test_create_execution_context_from(self):
        message = Message()
        spec_name = 'SPEC_NAME'
        spec_file_name = 'SPEC_FILE_NAME'
        scenario_name = 'SCENARIO_NAME'
        step_name = 'STEP_NAME'

        message.executionStartingRequest.\
            currentExecutionInfo.currentSpec.name = spec_name
        message.executionStartingRequest.\
            currentExecutionInfo.currentSpec.fileName = spec_file_name
        message.executionStartingRequest.\
            currentExecutionInfo.currentSpec.isFailed = True
        message.executionStartingRequest.\
            currentExecutionInfo.currentScenario.name = scenario_name
        message.executionStartingRequest.\
            currentExecutionInfo.currentScenario.isFailed = False
        message.executionStartingRequest.\
            currentExecutionInfo.currentStep.step.actualStepText = step_name
        message.executionStartingRequest.\
            currentExecutionInfo.currentStep.isFailed = True
        message.executionStartingRequest. \
            currentExecutionInfo.currentStep.errorMessage = "Error"
        message.executionStartingRequest. \
            currentExecutionInfo.currentStep.stackTrace = "stack trace"

        specification = Specification(spec_name, spec_file_name, True, [])
        scenario = Scenario(scenario_name, False, [])
        step = Step(step_name, True, "Error", "stack trace")

        context = ExecutionContext(specification, scenario, step)

        expected_execution_context = create_execution_context_from(
            message.executionStartingRequest.currentExecutionInfo)
        self.assertEqual(expected_execution_context, context)


class DecoratorTests(TestCase):
    def setUp(self):
        from tests.test_data import impl_stubs
        impl_stubs.step1()

    def test_step_decorator(self):
        steps = registry.steps()
        expected = {'Step 1', 'Step 2'}
        self.assertEqual(expected, set(steps))

    def test_continue_on_failure(self):
        step1 = registry.get_info_for('Step 1').impl
        step2 = registry.get_info_for('Step 2').impl

        self.assertEqual(
            registry.is_continue_on_failure(step1, RuntimeError()), False)
        self.assertEqual(
            registry.is_continue_on_failure(step2, RuntimeError()), True)

    def test_before_step_decorator(self):
        funcs = registry.before_step()
        expected = ['before_step1', 'before_step2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_after_step_decorator(self):
        funcs = registry.after_step()
        expected = ['after_step1']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_before_scenario_decorator(self):
        funcs = registry.before_scenario(['haha', 'hehe'])
        expected = ['before_scenario1', 'before_scenario2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_after_scenario_decorator(self):
        funcs = registry.after_scenario(['haha', 'hehe'])
        expected = ['after_scenario1', 'after_scenario2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_before_spec_decorator(self):
        funcs = registry.before_spec(['haha', 'hehe'])
        expected = ['before_spec1', 'before_spec2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_after_spec_decorator(self):
        funcs = registry.after_spec(['haha', 'hehe'])
        expected = ['after_spec1', 'after_spec2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_before_suite_decorator(self):
        funcs = registry.before_suite()
        expected = ['before_suite1']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_after_suite_decorator(self):
        funcs = registry.after_suite()
        expected = ['after_suite1', 'after_suite2']
        self.assertEqual(expected, [info.impl.__name__ for info in funcs])

    def test_screenshot_decorator(self):
        func = registry.screenshot_provider()
        expected = 'take_screenshot'
        self.assertEqual(expected, func.__name__)


class ScreenshotsTests(TestCase):
    def setUp(self):
        self.__old_screenshot_provider = registry.screenshot_provider()
        self.__is_screenshot_writer  = registry.is_screenshot_writer
        os.environ["gauge_screenshots_dir"] = tempfile.mkdtemp()

    def test_pending_screenshots(self):
        ScreenshotsStore.capture()
        pending_screenshots = ScreenshotsStore.pending_screenshots()
        self.assertEqual(1, len(pending_screenshots))
        self.assertTrue(os.path.exists(os.path.join(
            os.getenv("gauge_screenshots_dir"), pending_screenshots[0])))

    def test_clear(self):
        ScreenshotsStore.capture()
        ScreenshotsStore.clear()
        pending_screenshots = ScreenshotsStore.pending_screenshots()
        self.assertEqual([], pending_screenshots)

    def test_pending_screenshots_gives_only_those_screenshots_which_are_not_collected(self):
        ScreenshotsStore.capture()
        pending_screenshots = ScreenshotsStore.pending_screenshots()
        self.assertEqual(1, len(pending_screenshots))
        screenshot_file = pending_screenshots[0]
        pending_screenshots = ScreenshotsStore.pending_screenshots()
        self.assertEqual(0, len(pending_screenshots))
        ScreenshotsStore.capture()
        pending_screenshots = ScreenshotsStore.pending_screenshots()
        self.assertEqual(1, len(pending_screenshots))
        self.assertNotEqual(screenshot_file, pending_screenshots[0])

    def test_capture_shoould_vefify_screenshot_file_for_file_based_custom_screenshot(self):
        first_screenshot = os.path.join(
            os.getenv("gauge_screenshots_dir"), "screenshot{0}.png".format(uuid1()))
        second_screenshot = os.path.join(
            os.getenv("gauge_screenshots_dir"), "screenshot{0}.png".format(uuid1()))

        def returns_abs_path():
            return first_screenshot

        def returns_base_ath():
            return os.path.basename(second_screenshot)
        registry.set_screenshot_provider(returns_abs_path, True)
        ScreenshotsStore.capture()
        self.assertEqual([os.path.basename(first_screenshot)],
                         ScreenshotsStore.pending_screenshots())

        registry.set_screenshot_provider(returns_base_ath, True)
        ScreenshotsStore.capture()
        self.assertEqual([os.path.basename(second_screenshot)],
                         ScreenshotsStore.pending_screenshots())

    def tearDown(self):
        registry.set_screenshot_provider(
            self.__old_screenshot_provider, self.__is_screenshot_writer)


if __name__ == '__main__':
    main()
