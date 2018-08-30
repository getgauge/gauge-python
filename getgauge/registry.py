import os
import re
import sys
import tempfile
import logging
from subprocess import call


class StepInfo(object):
    def __init__(self, step_text, parsed_step_text, impl, file_name, span, has_alias=False, aliases=None):
        if aliases is None:
            aliases = []
        self.__step_text, self.__parsed_step_text, self.__impl = step_text, parsed_step_text, impl
        self.__file_name, self.__span, self.__has_alias = file_name, span, has_alias
        self.__aliases = aliases

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
    def aliases(self):
        return self.__aliases

    @property
    def file_name(self):
        return self.__file_name

    @property
    def span(self):
        # If span is callable, lazy load span on access
        if callable(self.__span):
            self.__span = self.__span()
        return self.__span


class MessagesStore:
    __messages = []

    @staticmethod
    def pending_messages():
        messages = MessagesStore.__messages
        MessagesStore.__messages = []
        return messages

    @staticmethod
    def write_message(message):
        MessagesStore.__messages.append(str(message))

    @staticmethod
    def clear():
        MessagesStore.__messages = []


class Registry(object):
    hooks = ['before_step', 'after_step', 'before_scenario', 'after_scenario', 'before_spec', 'after_spec',
             'before_suite', 'after_suite']

    def __init__(self):
        self.__screenshot_provider, self.__steps_map, self.__continue_on_failures = _take_screenshot, {}, {}
        for hook in Registry.hooks:
            self.__def_hook(hook)

    def __def_hook(self, hook):
        def get(self, tags=None):
            return _filter_hooks(tags, getattr(self, '__{}'.format(hook)))

        def add(self, func, tags=None):
            getattr(self, '__{}'.format(hook)).append(
                {'tags': tags, 'func': func})

        setattr(self.__class__, hook, get)
        setattr(self.__class__, 'add_{}'.format(hook), add)
        setattr(self, '__{}'.format(hook), [])

    def add_step(self, step_text, func, file_name, span=None, has_alias=False, aliases=None):
        if not isinstance(step_text, list):
            parsed_step_text = _get_step_value(step_text)
            info = StepInfo(step_text, parsed_step_text, func,
                            file_name, span, has_alias, aliases)
            self.__steps_map.setdefault(parsed_step_text, []).append(info)
            return
        for text in step_text:
            self.add_step(text, func, file_name, span, True, step_text)

    def steps(self):
        return [value[0].step_text for value in self.__steps_map.values()]

    def is_implemented(self, step_text):
        return self.__steps_map.get(step_text) is not None

    def has_multiple_impls(self, step_text):
        return len(self.__steps_map.get(step_text)) > 1

    def get_info_for(self, step_text):
        info = self.__steps_map.get(step_text)
        return info[0] if info is not None else StepInfo(None, None, None, None, None)

    def get_infos_for(self, step_text):
        return self.__steps_map.get(step_text)

    def set_screenshot_provider(self, func):
        self.__screenshot_provider = func

    def screenshot_provider(self):
        return self.__screenshot_provider

    def continue_on_failure(self, func, exceptions=None):
        self.__continue_on_failures[func] = exceptions or [AssertionError]

    def is_continue_on_failure(self, func, exception):
        if func in self.__continue_on_failures:
            for e in self.__continue_on_failures[func]:
                if issubclass(type(exception), e):
                    return True
        return False

    def get_step_positions(self, file_name):
        positions = []
        for step, infos in self.__steps_map.items():
            positions = positions + [{'stepValue': step, 'span': i.span}
                                     for i in infos if i.file_name == file_name]
        return positions

    def remove_steps(self, file_name):
        new_map = {}
        for step, infos in self.__steps_map.items():
            filtered_info = [i for i in infos if i.file_name != file_name]
            if len(filtered_info) > 0:
                new_map[step] = filtered_info
        self.__steps_map = new_map

    def clear(self):
        self.__steps_map, self.__continue_on_failures = {}, {}
        for hook in Registry.hooks:
            setattr(self, '__{}'.format(hook), [])


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


def _get_step_value(step_text):
    return re.sub('(<.*?>)', '{}', step_text)


def _take_screenshot():
    temp_file = os.path.join(tempfile.gettempdir(), 'screenshot.png')
    try:
        call(['gauge_screenshot', temp_file])
        _file = open(temp_file, 'r+b')
        data = _file.read()
        _file.close()
        return data
    except Exception as err:
        logging.error(
            "\nFailed to take screenshot using gauge_screenshot.\n{0}".format(err))
    except:
        logging.error("\nFailed to take screenshot using gauge_screenshot.\n{0}".format(
            sys.exc_info()[0]))
    return str.encode("")


registry = Registry()


class ScreenshotsStore:
    __screenshots = []

    @staticmethod
    def pending_screenshots():
        screenshots = ScreenshotsStore.__screenshots
        ScreenshotsStore.__screenshots = []
        return screenshots

    @staticmethod
    def capture():
        ScreenshotsStore.__screenshots.append(registry.screenshot_provider()())

    @staticmethod
    def clear():
        ScreenshotsStore.__screenshots = []
