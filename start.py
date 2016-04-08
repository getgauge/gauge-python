#! /usr/bin/env python
import sys

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
