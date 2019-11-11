import os
import platform
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from os import environ, path
from threading import Timer

import grpc
import ptvsd
from getgauge import handlers, logger, processor
from getgauge.impl_loader import copy_skel_files
from getgauge.messages import runner_pb2_grpc
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dirs

PLUGIN_JSON = 'python.json'
VERSION = 'version'
ATTACH_DEBUGGER_EVENT = 'Runner Ready for Debugging'


def main():
    logger.info("Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        logger.debug("Initilizing gauge project.")
        copy_skel_files()
    else:
        load_implementations()
        start()


def load_implementations():
    d = get_step_impl_dirs()
    logger.debug(
        "Loading step implemetations from {} dirs.".format(', '.join(d)))
    for impl_dir in d:
        if not path.exists(impl_dir):
            logger.error('can not load implementations from {}. {} does not exist.'.format(
                impl_dir, impl_dir))
    load_files(d)


def _handle_detached():
    logger.info("No debugger attached. Stopping the execution.")
    os._exit(1)


def start():
    if environ.get('DEBUGGING'):
        ptvsd.enable_attach(address=(
            '127.0.0.1', int(environ.get('DEBUG_PORT'))))
        print(ATTACH_DEBUGGER_EVENT)
        t = Timer(int(environ.get("debugger_wait_time", 30)), _handle_detached)
        t.start()
        ptvsd.wait_for_attach()
        t.cancel()
    logger.debug('Starting grpc server..')
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    p = server.add_insecure_port('127.0.0.1:0')
    handler = handlers.RunnerServiceHandler(server)
    runner_pb2_grpc.add_RunnerServicer_to_server(handler, server)
    logger.info('Listening on port:{}'.format(p))
    server.start()
    t = threading.Thread(
            name="listener", target=handler.wait_for_kill_event)
    t.start()
    t.join()
    os._exit(0)


if __name__ == '__main__':
    main()
