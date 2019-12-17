import sys
import warnings
from getgauge.registry import registry, MessagesStore, ScreenshotsStore

if sys.version_info[0] is 3:
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


def step(step_text):
    def _step(func):
        f_code = sys._getframe().f_back.f_code
        span = {'start': f_code.co_firstlineno,
                'startChar': 0, 'end': 0, 'endChar': 0}
        registry.add_step(step_text, func, f_code.co_filename, span)
        return func

    return _step


def continue_on_failure(obj):
    return _define_wrapper(obj, registry.continue_on_failure)


def before_suite(obj=None):
    return _define_wrapper(obj, registry.add_before_suite)


def after_suite(obj=None):
    return _define_wrapper(obj, registry.add_after_suite)


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
    _warn_screenshot_deprecation('screenshot', 'custom_screenshot_writer')
    registry.set_screenshot_provider(func, False)
    return func


def custom_screen_grabber(func):
    _warn_screenshot_deprecation('custom_screen_grabber', 'custom_screenshot_writer')
    registry.set_screenshot_provider(func, False)
    return func

def custom_screenshot_writer(func):
    registry.set_screenshot_provider(func, True)
    return func

def _warn_screenshot_deprecation(old_function, new_function):
    warnings.warn(
        "'{0}' is deprecated in favour of '{1}'".format(old_function, new_function),
        DeprecationWarning, stacklevel=3)
    warnings.simplefilter('default', DeprecationWarning)


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
                                                                                               str(
                                                                                                   self.is_failing),
                                                                                               ", ".join(
                                                                                                   self.tags),
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
    def __init__(self, text, is_failing, message="", stacktrace=""):
        self.__stacktrace = stacktrace
        self.__error_message = message
        self.__text = text
        self.__is_failing = is_failing

    @property
    def text(self):
        return self.__text

    @property
    def is_failing(self):
        return self.__is_failing

    @property
    def error_message(self):
        return self.__error_message

    @property
    def stacktrace(self):
        return self.__stacktrace

    def __str__(self):
        s = "Step: {{ text: {}, is_failing: {}, error_message: {}, stacktrace: {} }}"
        return s.format(self.text, str(self.is_failing), str(self.error_message), str(self.stacktrace))

    def __eq__(self, other):
        return self.__str__() == other.__str__()


class Messages:
    @staticmethod
    def write_message(message):
        MessagesStore.write_message(message)


class DictObject(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(
                self.__class__.__name__, name))

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(
                self.__class__.__name__, name))


class DataStoreContainer(object):
    def __init__(self):
        self.__scenario = DictObject()
        self.__spec = DictObject()
        self.__suite = DictObject()

    @property
    def scenario(self):
        return self.__scenario

    @property
    def spec(self):
        return self.__spec

    @property
    def suite(self):
        return self.__suite


data_store = DataStoreContainer()


class DataStore:
    def __init__(self, data_store=None):
        if data_store is None:
            data_store = {}
        self.__data_store = data_store

    def get(self, key):
        return self.__data_store[key]

    def put(self, key, value):
        self.__data_store[key] = value

    def is_present(self, key):
        return key in self.__data_store

    def clear(self):
        self.__data_store.clear()

    def __eq__(self, other):
        return self.__data_store == other.__data_store


def _warn_datastore_deprecation(store_type):
    warnings.warn(
        "'DataStoreFactory.{0}_data_store()' is deprecated in favour of 'data_store.{0}'".format(
            store_type),
        DeprecationWarning, stacklevel=3)
    warnings.simplefilter('default', DeprecationWarning)


class DataStoreFactory:
    __scenario_data_store = DataStore(data_store.scenario)
    __spec_data_store = DataStore(data_store.spec)
    __suite_data_store = DataStore(data_store.suite)

    @staticmethod
    def scenario_data_store():
        _warn_datastore_deprecation("scenario")
        return DataStoreFactory.__scenario_data_store

    @staticmethod
    def spec_data_store():
        _warn_datastore_deprecation("spec")
        return DataStoreFactory.__spec_data_store

    @staticmethod
    def suite_data_store():
        _warn_datastore_deprecation("suite")
        return DataStoreFactory.__suite_data_store


def create_execution_context_from(current_execution_info):
    return ExecutionContext(
        Specification(current_execution_info.currentSpec.name, current_execution_info.currentSpec.fileName,
                      current_execution_info.currentSpec.isFailed, current_execution_info.currentSpec.tags),
        Scenario(current_execution_info.currentScenario.name, current_execution_info.currentScenario.isFailed,
                 current_execution_info.currentScenario.tags),
        Step(current_execution_info.currentStep.step.actualStepText, current_execution_info.currentStep.isFailed,
             current_execution_info.currentStep.errorMessage, current_execution_info.currentStep.stackTrace)
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


class Screenshots:
    @staticmethod
    def capture_screenshot():
        ScreenshotsStore.capture()
