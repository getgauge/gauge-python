#! /usr/bin/env python
import sys

assert sys.version_info > (3, 0), 'Getgauge package Requires python3 or greater. Make sure `python --version` outputs 3.x version'

from getgauge import connection, processor
from getgauge.impl_loader import load_impls, copy_skel_files


def main():
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        s = connection.connect()
        load_impls()
        processor.dispatch_messages(s)


if __name__ == '__main__':
    main()
