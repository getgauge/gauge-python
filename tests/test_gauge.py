import unittest

from getgauge.messages.messages_pb2 import Message
from getgauge.python import Messages, DataStore, DataStoreFactory, Table, Specification, Scenario, Step, \
    ExecutionContext, \
    create_execution_context_from
from getgauge.registry import registry

registry.clear()


class MessagesTests(unittest.TestCase):
    def test_pending_messages(self):
        messages = ["HAHAHAH", "HAHAHAH1", "HAHAHAH2", "HAHAHAH3"]
        for message in messages:
            Messages.write_message(message)
        pending_messages = Messages.pending_messages()
        self.assertEqual(messages, pending_messages)

    def test_pending_messages_gives_only_those_messages_which_are_not_reported(self):
        messages = ["HAHAHAH", "HAHAHAH1", "HAHAHAH2", "HAHAHAH3"]
        for message in messages:
            Messages.write_message(message)
        pending_messages = Messages.pending_messages()
        self.assertEqual(messages, pending_messages)

        pending_messages = Messages.pending_messages()

        self.assertEqual([], pending_messages)

        messages = ["HAHAHAH", "HAHAHAH1"]
        for message in messages:
            Messages.write_message(message)

        pending_messages = Messages.pending_messages()

        self.assertEqual(messages, pending_messages)


class DataStoreTests(unittest.TestCase):
    def test_data_store(self):
        store = DataStore()
        values = {'key': 'HAHAHAH', 'key1': 'HAHAHAH1', 'key2': 'HAHAHAH2', 'key3': 'HAHAHAH3'}
        for value in values:
            store.put(value, value)

        for value in values:
            store.put(value, values[value])

        for value in values:
            self.assertEqual(store.get(value), values[value])

    def test_data_store_clear(self):
        store = DataStore()
        values = {'key': 'HAHAHAH', 'key1': 'HAHAHAH1', 'key2': 'HAHAHAH2', 'key3': 'HAHAHAH3'}
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

        store.put("a", "b")
        store1.put("a", "b")

        self.assertEqual(store, store1)

        store.put("b", "b")
        store1.put("c", "b")

        self.assertNotEqual(store, store1)


class DataStoreFactoryTests(unittest.TestCase):
    def test_data_store_factory(self):
        scenario_data_store = DataStoreFactory.get_scenario_data_store()
        spec_data_store = DataStoreFactory.get_spec_data_store()
        suite_data_store = DataStoreFactory.get_suite_data_store()

        data_store = DataStore()

        self.assertEqual(data_store, scenario_data_store)
        self.assertEqual(data_store, spec_data_store)
        self.assertEqual(data_store, suite_data_store)


class ProtoTable:
    def __init__(self, table_dict):
        self.headers = ProtoRow(table_dict['headers']['cells'])
        self.rows = [ProtoRow(row['cells']) for row in table_dict['rows']]


class ProtoRow:
    def __init__(self, cells):
        self.cells = cells


class TableTests(unittest.TestCase):
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
        self.assertEqual(expected_column_1, table.get_column_values_with_index(1))
        self.assertEqual(expected_column_2, table.get_column_values_with_index(2))
        self.assertEqual(expected_column_1, table.get_column_values_with_name(headers[0]))
        self.assertEqual(expected_column_2, table.get_column_values_with_name(headers[1]))
        for row in expected_rows:
            self.assertEqual(row, table.get_row(expected_rows.index(row) + 1))

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


class SpecificationTests(unittest.TestCase):
    def test_Specification(self):
        name = "NAME"
        file_name = "FILE_NAME"
        tags = ["TAGS"]
        specification = Specification(name, file_name, False, tags)

        self.assertEqual(specification.name, name)
        self.assertEqual(specification.file_name, file_name)
        self.assertEqual(specification.is_failing, False)
        self.assertEqual(specification.tags, tags)

    def test_Specification_equality(self):
        name = "NAME"
        file_name = "FILE_NAME"
        tags = ["TAGS"]
        specification = Specification(name, file_name, False, tags)
        specification1 = Specification(name, file_name, False, tags)

        self.assertEqual(specification, specification1)


class ScenarioTests(unittest.TestCase):
    def test_Scenario(self):
        name = "NAME3"
        tags = ["TAGS"]
        scenario = Scenario(name, False, tags)

        self.assertEqual(scenario.name, name)
        self.assertEqual(scenario.is_failing, False)
        self.assertEqual(scenario.tags, tags)

    def test_Scenario_equality(self):
        name = "NAME2"
        tags = ["TAGS"]
        scenario = Scenario(name, False, tags)
        scenario1 = Scenario(name, False, tags)

        self.assertEqual(scenario, scenario1)


class StepTests(unittest.TestCase):
    def test_Step(self):
        name = "NAME1"
        step = Step(name, False)

        self.assertEqual(step.text, name)
        self.assertEqual(step.is_failing, False)

    def test_Step_equality(self):
        name = "NAME1"
        step = Step(name, False)
        step1 = Step(name, False)

        self.assertEqual(step, step1)


class ExecutionContextTests(unittest.TestCase):
    def test_ExecutionContextTests(self):
        name = "NAME"
        file_name = "FILE_NAME"
        tags = ["TAGS"]
        specification = Specification(name, file_name, False, tags)
        scenario = Scenario(name, False, tags)
        step = Step(name, False)

        context = ExecutionContext(specification, scenario, step)
        self.assertEqual(specification, context.specification)
        self.assertEqual(scenario, context.scenario)
        self.assertEqual(step, context.step)

    def test_ExecutionContextTests_equality(self):
        name = "NAME"
        file_name = "FILE_NAME"
        tags = ["TAGS"]
        specification = Specification(name, file_name, False, tags)
        scenario = Scenario(name, False, tags)
        step = Step(name, False)

        context = ExecutionContext(specification, scenario, step)
        context1 = ExecutionContext(specification, scenario, step)

        self.assertEqual(context, context1)

    def test_create_execution_context_from(self):
        message = Message()
        spec_name, spec_file_name, scenario_name, step_name = "SPEC_NAME", "SPEC_FILE_NAME", "SCENARIO_NAME", "STEP_NAME"
        message.executionStartingRequest.currentExecutionInfo.currentSpec.name = spec_name
        message.executionStartingRequest.currentExecutionInfo.currentSpec.fileName = spec_file_name
        message.executionStartingRequest.currentExecutionInfo.currentSpec.isFailed = True
        message.executionStartingRequest.currentExecutionInfo.currentScenario.name = scenario_name
        message.executionStartingRequest.currentExecutionInfo.currentScenario.isFailed = False
        message.executionStartingRequest.currentExecutionInfo.currentStep.step.actualStepText = step_name
        message.executionStartingRequest.currentExecutionInfo.currentStep.isFailed = True

        specification = Specification(spec_name, spec_file_name, True, [])
        scenario = Scenario(scenario_name, False, [])
        step = Step(step_name, True)

        context = ExecutionContext(specification, scenario, step)

        expected_execution_context = create_execution_context_from(
            message.executionStartingRequest.currentExecutionInfo)
        self.assertEqual(expected_execution_context, context)


class DecoratorTests(unittest.TestCase):
    def setUp(self):
        import test_data.impl_stub

    def test_step_decorator(self):
        steps = registry.all_steps()
        expected = ['Step 1', 'Step 2']
        self.assertEqual(expected, steps)

    def test_before_step_decorator(self):
        funcs = registry.before_step()
        expected = ['before_step1', 'before_step2']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_after_step_decorator(self):
        funcs = registry.after_step()
        expected = ['after_step1']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_before_scenario_decorator(self):
        funcs = registry.before_scenario(['haha', 'hehe'])
        expected = ['before_scenario1', 'before_scenario2']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_after_scenario_decorator(self):
        funcs = registry.after_scenario(['haha', 'hehe'])
        expected = ['after_scenario1', 'after_scenario2']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_before_spec_decorator(self):
        funcs = registry.before_spec(['haha', 'hehe'])
        expected = ['before_spec1', 'before_spec2']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_after_spec_decorator(self):
        funcs = registry.after_spec(['haha', 'hehe'])
        expected = ['after_spec1', 'after_spec2']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_before_suite_decorator(self):
        funcs = registry.before_suite()
        expected = ['before_suite1']
        self.assertEqual(expected, [func.func_name for func in funcs])

    def test_after_suite_decorator(self):
        funcs = registry.after_suite()
        expected = ['after_suite1', 'after_suite2']
        self.assertEqual(expected, [func.func_name for func in funcs])


if __name__ == '__main__':
    unittest.main()
