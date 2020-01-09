import inspect
import os
import re
import sys
from uuid import uuid1
from subprocess import call

from getgauge import logger


class StepInfo(object):
    def __init__(self, step_text, parsed_step_text, impl, file_name, span, has_alias=False, aliases=None):
        if aliases is None:
            aliases = []
        self.__step_text, self.__parsed_step_text, self.__impl = step_text, parsed_step_text, impl
        self.__file_name, self.__span, self.__has_alias = file_name, span, has_alias
        self.__instance = None
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
    def instance(self):
        return self.__instance

    @instance.setter
    def instance(self, value):
        self.__instance = value

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


class HookInfo(object):
    def __init__(self, tags, impl, file_name):
        self.__tags, self.__impl, self.__file_name = tags, impl, file_name
        self.__instance = None

    @property
    def tags(self):
        return self.__tags

    @property
    def impl(self):
        return self.__impl

    @property
    def file_name(self):
        return self.__file_name

    @property
    def instance(self):
        return self.__instance

    @instance.setter
    def instance(self, value):
        self.__instance = value


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
        self.is_screenshot_writer = True
        for hook in Registry.hooks:
            self.__def_hook(hook)

    def __def_hook(self, hook):
        def get(self, tags=None):
            return _filter_hooks(tags, getattr(self, '__{}'.format(hook)))

        def add(self, func=None, tags=None, file_name=""):
            if not isinstance(func, str):
                file_name = inspect.getsourcefile(func)
            getattr(self, '__{}'.format(hook)).append(
                HookInfo(tags, func, file_name))

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

    def set_screenshot_provider(self, func, is_writer):
        self.__screenshot_provider = func
        self.is_screenshot_writer = is_writer

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

    def _get_all_hooks(self, file_name):
        all_hooks = []
        for hook in self.hooks:
            all_hooks = all_hooks + \
                        [h for h in getattr(self, "__{}".format(hook))
                         if h.file_name == file_name]
        return all_hooks

    def get_all_methods_in(self, file_name):
        methods = []
        for _, infos in self.__steps_map.items():
            methods = methods + [i for i in infos if i.file_name == file_name]
        return methods + self._get_all_hooks(file_name)

    def is_file_cached(self, file_name):
        for _, infos in self.__steps_map.items():
            if any(i.file_name == file_name for i in infos):
                return True
        return False

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
        hook_tags = hook.tags
        if hook_tags is None:
            filtered_hooks.append(hook)
            continue
        for tag in tags:
            hook_tags = hook_tags.replace('<{}>'.format(tag), 'True')
        if eval(re.sub('<[^<]+?>', 'False', hook_tags)):
            filtered_hooks.append(hook)
    return filtered_hooks


def _get_step_value(step_text):
    return re.sub('(<.*?>)', '{}', step_text)


def _take_screenshot():
    temp_file = _uniqe_screenshot_file()
    try:
        call(['gauge_screenshot', temp_file])
        return os.path.basename(temp_file)
    except Exception as err:
        logger.error(
            "\nFailed to take screenshot using gauge_screenshot.\n{0}".format(err))
    except:
        logger.error("\nFailed to take screenshot using gauge_screenshot.\n{0}".format(
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
        screenshot = ScreenshotsStore.capture_to_file()
        ScreenshotsStore.__screenshots.append(screenshot)

    @staticmethod
    def capture_to_file():
        if not registry.is_screenshot_writer:
            screenshot_file = _uniqe_screenshot_file()
            content = registry.screenshot_provider()()
            file = open(screenshot_file, "wb")
            file.write(content)
            file.close()
            return os.path.basename(screenshot_file)
        screenshot_file = registry.screenshot_provider()()
        if(not os.path.isabs(screenshot_file)):
            screenshot_file = os.path.join(_screenshots_dir(), screenshot_file)
        if(not os.path.exists(screenshot_file)):
            logger.warning("Screenshot file {0} does not exists.".format(screenshot_file))
        return os.path.basename(screenshot_file)

    @staticmethod
    def clear():
        ScreenshotsStore.__screenshots = []

def _uniqe_screenshot_file():
    return os.path.join(_screenshots_dir(), "screenshot-{0}.png".format(uuid1().int))

def _screenshots_dir():
    return os.getenv('gauge_screenshots_dir')