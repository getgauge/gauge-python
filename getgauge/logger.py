import json
import sys


def debug(message):
    _print('debug', message)


def info(message):
    _print('info', message)


def error(message):
    _print('error', message, True)


def warning(message):
    _print('warning', message)


def fatal(message):
    _print('fatal', message, True)


def _print(level, message, is_error=False):
    stream = sys.stdout if not is_error else sys.stderr
    stream.write("{}\n".format(json.dumps({"logLevel": level, "message": message})))
