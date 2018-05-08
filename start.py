import json
import logging
import os
import platform
import sys
import threading
from concurrent import futures
from distutils import version
from os import path
from subprocess import Popen, PIPE

import grpc
import pkg_resources

from getgauge import connection, processor
from getgauge import lsp_server
from getgauge.impl_loader import copy_skel_files
from getgauge.messages import lsp_pb2_grpc
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dir

PLUGIN_JSON = 'python.json'
VERSION = 'version'


def main():
    _init_logger()
    logging.info("Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        assert_versions()
        load_implementations()
        start()


def assert_versions():
    python_plugin_version = get_version()
    getgauge_version = version.LooseVersion(pkg_resources.get_distribution('getgauge').version)
    if (list(map(int, python_plugin_version.split(".")[0:3])) != getgauge_version.version[0:3]) or (
            'dev' in getgauge_version.version and 'nightly' not in python_plugin_version) or (
            'dev' not in getgauge_version.version and 'nightly' in python_plugin_version):
        show_error_exit(python_plugin_version, getgauge_version)
    if 'dev' in getgauge_version.version and 'nightly' in python_plugin_version:
        if str(getgauge_version.version.pop()) not in python_plugin_version.replace("-", ""):
            show_error_exit(python_plugin_version, getgauge_version)


def show_error_exit(python_plugin_version, getgauge_version):
    logging.fatal('Gauge-python({}) is not compatible with getgauge({}). Please install compatible versions.\n'.format(
        python_plugin_version, getgauge_version))
    exit(1)


def get_version():
    proc = Popen(['gauge', '-v', '--machine-readable'], stdout=PIPE, stderr=PIPE)
    out, _ = proc.communicate()
    data = json.loads(str(out.decode()))
    for plugin in data['plugins']:
        if plugin['name'] == 'python':
            return plugin['version']
    return ''


def load_implementations():
    d = get_step_impl_dir()
    if path.exists(d):
        load_files(d)
    else:
        logging.error('can not load implementations from {}. {} does not exist.'.format(d, d))


def start():
    if os.getenv('GAUGE_LSP_GRPC'):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        p = server.add_insecure_port('127.0.0.1:0')
        handler = lsp_server.LspServerHandler(server)
        lsp_pb2_grpc.add_lspServiceServicer_to_server(handler, server)
        logging.info('Listening on port:{}'.format(p))
        server.start()
        wait_thread = threading.Thread(name="listener", target=handler.wait_till_terminated)
        wait_thread.start()
        wait_thread.join()
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
