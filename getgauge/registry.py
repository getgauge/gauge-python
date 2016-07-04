import os
import re
import tempfile
from subprocess import call

from getgauge.api import get_step_value


class StepInfo(object):
    def __init__(self, step_text, parsed_step_text, impl, file_name, line_number, has_alias=False):
        self.__step_text = step_text
        self.__parsed_step_text = parsed_step_text
        self.__impl = impl
        self.__file_name = file_name
        self.__line_number = line_number
        self.__has_alias = has_alias

    @property
    def step_text(self):
        return self.__step_text

    @property
    def parsed_step_text(self):
        return self.__parsed_step_text

    @property
    def impl(self):
        return self.__impl

    @property
    def has_alias(self):
        return self.__has_alias

    @property
    def file_name(self):
        return self.__file_name

    @property
    def line_number(self):
        return self.__line_number


class _MessagesStore:
    __messages = []

    @staticmethod
    def pending_messages():
        messages = _MessagesStore.__messages
        _MessagesStore.__messages = []
        return messages

    @staticmethod
    def write_message(message):
        _MessagesStore.__messages.append(message)

    @staticmethod
    def clear():
        _MessagesStore.__messages = []


def _take_screenshot():
    temp_file = os.path.join(tempfile.gettempdir(), 'screenshot.png')
    call(['gauge_screenshot', temp_file])
    _file = open(temp_file, 'r+b')
    data = _file.read()
    _file.close()
    return data


class Registry(object):
    hooks = ['before_step', 'after_step', 'before_scenario', 'after_scenario', 'before_spec', 'after_spec',
             'before_suite', 'after_suite']

    def __init__(self):
        self.__screenshot_provider = _take_screenshot
        self.__steps_map = {}
        for hook in Registry.hooks:
            self.def_hook_methods(hook)

    def def_hook_methods(self, hook):
        def get(self, tags=None):
            return _filter_hooks(tags, getattr(self, '__{}'.format(hook)))

        def add(self, func, tags=None):
            getattr(self, '__{}'.format(hook)).append({'tags': tags, 'func': func})

        setattr(self.__class__, hook, get)
        setattr(self.__class__, 'add_{}'.format(hook), add)
        setattr(self, '__{}'.format(hook), [])

    def add_step_definition(self, step_text, func, file_name, line_number=-1, has_alias=False):
        if not isinstance(step_text, list):
            parsed_step_text = get_step_value(step_text)
            self.__steps_map.setdefault(parsed_step_text, []).append(StepInfo(step_text, parsed_step_text, func, file_name, line_number, has_alias))
            return
        for text in step_text:
            self.add_step_definition(text, func, file_name, line_number, True)

    def all_steps(self):
        return [value[0].step_text for value in self.__steps_map.values()]

    def is_step_implemented(self, step_text):
        return self.__steps_map.get(step_text) is not None

    def has_multiple_impls(self, step_text):
        return len(self.__steps_map.get(step_text)) > 1

    def get_info(self, step_text):
        info = self.__steps_map.get(step_text)
        return info[0] if info is not None else StepInfo(None, None, None, None, None)

    def get_infos(self, step_text):
        return self.__steps_map.get(step_text)

    def set_screenshot_provider(self, func):
        self.__screenshot_provider = func

    def screenshot_provider(self):
        return self.__screenshot_provider

    def clear(self):
        self.__steps_map = {}
        for hook in Registry.hooks:
            setattr(self, '__{}'.format(hook), [])


registry = Registry()


def _filter_hooks(tags, hooks):
    filtered_hooks = []
    for hook in hooks:
        hook_tags = hook['tags']
        if hook_tags is None:
            filtered_hooks.append(hook['func'])
            continue
        for tag in tags:
            hook_tags = hook_tags.replace('<{}>'.format(tag), 'True')
        if eval(re.sub('<[^<]+?>', 'False', hook_tags)):
            filtered_hooks.append(hook['func'])
    return filtered_hooks
