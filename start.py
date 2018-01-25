import platform
import sys

from colorama import Style, init

from getgauge import connection, processor
from getgauge.impl_loader import copy_skel_files
from getgauge.static_loader import load_files
from getgauge.util import get_step_impl_dir


def main():
    init(autoreset=True, strip=False)
    print(Style.DIM + "Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        s = connection.connect()
        load_files(get_step_impl_dir())
        processor.dispatch_messages(s)


if __name__ == '__main__':
    main()
