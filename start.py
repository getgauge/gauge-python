import os
import platform
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from os import path

import grpc
from getgauge import handlers, logger, lsp_server, processor
from getgauge.impl_loader import copy_skel_files
from getgauge.messages import lsp_pb2_grpc, runner_pb2_grpc
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dirs

PLUGIN_JSON = 'python.json'
VERSION = 'version'


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


def start():
    logger.debug('Starting grpc server..')
    server = grpc.server(ThreadPoolExecutor(max_workers=1))
    p = server.add_insecure_port('127.0.0.1:0')
    if os.getenv('GAUGE_LSP_GRPC'):
        handler = lsp_server.LspServerHandler(server)
        lsp_pb2_grpc.add_lspServiceServicer_to_server(handler, server)
    else:
        handler = handlers.RunnerServiceHandler(server)
        runner_pb2_grpc.add_RunnerServicer_to_server(handler, server)
    logger.info('Listening on port:{}'.format(p))
    server.start()
    wait_thread = threading.Thread(
        name="listener", target=handler.wait_till_terminated)
    wait_thread.start()
    wait_thread.join()


if __name__ == '__main__':
    main()
