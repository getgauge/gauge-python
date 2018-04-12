import logging
import os
import platform
import sys
from concurrent import futures
from os import path

import grpc

from getgauge import connection, processor
from getgauge import lsp_server
from getgauge.impl_loader import copy_skel_files
from getgauge.messages import lsp_pb2_grpc
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dir


def main():
    _init_logger()
    logging.info("Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        load_implementations()
        start()


def load_implementations():
    d = get_step_impl_dir()
    if path.exists(d):
        load_files(d)
    else:
        logging.error('can not load implementations from {}. {} does not exist.'.format(d, d))


def start():
    if os.getenv('GAUGE_LSP_GRPC'):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        p = server.add_insecure_port('127.0.0.1:0')
        lsp_pb2_grpc.add_lspServiceServicer_to_server(lsp_server.LspServerHandler(server), server)
        server.start()
        logging.info('Listening on port:{}'.format(p))
        while True:
            pass
    else:
        s = connection.connect()
        processor.dispatch_messages(s)


def _init_logger():
    if os.getenv('IS_DAEMON'):
        f = '%(asctime)s.%(msecs)03d %(message)s'
        logging.basicConfig(stream=sys.stdout, format=f, level=logging.DEBUG, datefmt='%H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.DEBUG)


if __name__ == '__main__':
    main()
