import inspect
import sys

from getgauge.registry import registry, _MessagesStore


def step(step_text):
    def _step(func):
        f_back = sys._getframe().f_back
        registry.add_step(step_text, func, f_back.f_code.co_filename, inspect.getsourcelines(func)[1])
        return func

    return _step


def continue_on_failure(obj):
    return _define_wrapper(obj, registry.continue_on_failure)


def before_suite(func):
    registry.add_before_suite(func)
    return func


def after_suite(func):
    registry.add_after_suite(func)
    return func


def before_scenario(obj=None):
    return _define_wrapper(obj, registry.add_before_scenario)


def after_scenario(obj=None):
    return _define_wrapper(obj, registry.add_after_scenario)


def before_spec(obj=None):
    return _define_wrapper(obj, registry.add_before_spec)


def after_spec(obj=None):
    return _define_wrapper(obj, registry.add_after_spec)


def before_step(obj=None):
    return _define_wrapper(obj, registry.add_before_step)


def after_step(obj=None):
    return _define_wrapper(obj, registry.add_after_step)


def screenshot(func):
    registry.set_screenshot_provider(func)
    return func


class Table:
    def __init__(self, proto_table):
        self.__headers = proto_table.headers.cells
        self.__rows = proto_table.rows

    @property
    def headers(self):
        return self.__headers

    @property
    def rows(self):
        return [row.cells for row in self.__rows]

    def get_row(self, index):
        return self.__rows[index - 1].cells

    def get_column_values_with_name(self, name):
        index = list(self.__headers).index(name)
        return self.get_column_values_with_index(index + 1)

    def get_column_values_with_index(self, index):
        return [row.cells[index - 1] for row in self.__rows]

    def __str__(self):
        table = [""] * (len(self.__rows) + 2)
        for header in self.__headers:
            values = [header, ""] + self.get_column_values_with_name(header)
            m_length = max(map(len, values))
            values[1] = "-" * m_length
            values = [value.ljust(m_length) for value in values]
            for i, value in enumerate(values):
                table[i] = table[i] or []
                table[i].append(value)
        return "\n".join(["|{}|".format("|".join(row)) for row in table])

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __getitem__(self, i):
        return self.get_row(i + 1)

    def __iter__(self):
        return self.rows.__iter__()


class ExecutionContext:
    def __init__(self, specification, scenario, step):
        self.__step = step
        self.__specification = specification
        self.__scenario = scenario

    @property
    def specification(self):
        return self.__specification

    @property
    def scenario(self):
        return self.__scenario

    @property
    def step(self):
        return self.__step

    def __str__(self):
        return 'ExecutionInfo: {{ {}, {}, {} }}'.format(self.specification.__str__(), self.scenario.__str__(),
                                                        self.step.__str__())

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Specification:
    def __init__(self, name, file_name, is_failing, tags):
        self.__name = name
        self.__file_name = file_name
        self.__is_failing = is_failing
        self.__tags = tags

    @property
    def name(self):
        return self.__name

    @property
    def file_name(self):
        return self.__file_name

    @property
    def is_failing(self):
        return self.__is_failing

    @property
    def tags(self):
        return self.__tags

    def __str__(self):
        return "Specification: {{ name: {}, is_failing: {}, tags: {}, file_name: {} }}".format(self.name,
                                                                                               str(self.is_failing),
                                                                                               ", ".join(self.tags),
                                                                                               self.file_name)

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Scenario:
    def __init__(self, name, is_failing, tags):
        self.__name = name
        self.__is_failing = is_failing
        self.__tags = tags

    @property
    def name(self):
        return self.__name

    @property
    def is_failing(self):
        return self.__is_failing

    @property
    def tags(self):
        return self.__tags

    def __str__(self):
        return "Scenario: {{ name: {}, is_failing: {}, tags: {} }}".format(self.name, str(self.is_failing),
                                                                           ", ".join(self.tags))

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Step:
    def __init__(self, text, is_failing):
        self.__text = text
        self.__is_failing = is_failing

    @property
    def text(self):
        return self.__text

    @property
    def is_failing(self):
        return self.__is_failing

    def __str__(self):
        return "Step: {{ text: {}, is_failing: {} }}".format(self.text, str(self.is_failing))

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Messages:
    @staticmethod
    def write_message(message):
        _MessagesStore.write_message(message)


class DataStore:
    def __init__(self):
        self.__data_store = {}

    def get(self, key):
        return self.__data_store[key]

    def put(self, key, value):
        self.__data_store[key] = value

    def is_present(self, key):
        return key in self.__data_store

    def clear(self):
        self.__data_store = {}

    def __eq__(self, other):
        return self.__data_store == other.__data_store


class DataStoreFactory:
    __scenario_data_store = DataStore()
    __spec_data_store = DataStore()
    __suite_data_store = DataStore()

    @staticmethod
    def scenario_data_store():
        return DataStoreFactory.__scenario_data_store

    @staticmethod
    def spec_data_store():
        return DataStoreFactory.__spec_data_store

    @staticmethod
    def suite_data_store():
        return DataStoreFactory.__suite_data_store


def create_execution_context_from(current_execution_info):
    return ExecutionContext(
        Specification(current_execution_info.currentSpec.name, current_execution_info.currentSpec.fileName,
                      current_execution_info.currentSpec.isFailed, current_execution_info.currentSpec.tags),
        Scenario(current_execution_info.currentScenario.name, current_execution_info.currentScenario.isFailed,
                 current_execution_info.currentScenario.tags),
        Step(current_execution_info.currentStep.step.actualStepText, current_execution_info.currentStep.isFailed)
    )


def _wrapper(*args, **kwargs):
    pass


def _define_wrapper(obj, callback):
    if hasattr(obj, '__call__'):
        callback(obj, None)
        return obj

    def func(function):
        callback(function, obj)
        return function

    return func
