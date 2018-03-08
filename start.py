import platform
import sys
import logging
import os

from os import path
from getgauge import connection, processor
from getgauge.impl_loader import copy_skel_files
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dir


def main():
    _init_logger()
    logging.info("Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        s = connection.connect()
        dir = get_step_impl_dir()
        if path.exists(dir):
            load_files(dir)
        else:
            logging.error('can not load implementations from {}. {} does not exist.'.format(dir, dir))
        processor.dispatch_messages(s)


def _init_logger():
    if os.getenv("IS_DAEMON"):
        logging.basicConfig(stream=sys.stdout, format='%(asctime)s.%(msecs)03d %(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.DEBUG)


if __name__ == '__main__':
    main()
