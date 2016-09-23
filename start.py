import platform
import sys

from colorama import Style, init

from getgauge import api
from getgauge import connection, processor
from getgauge.impl_loader import load_impls, copy_skel_files


def main():
    init(autoreset=True, strip=False)
    print(Style.DIM + "Python: {}".format(platform.python_version()))
    if sys.argv[1] == "--init":
        copy_skel_files()
    else:
        s = connection.connect()
        api.connect_to_api()
        load_impls()
        api.close_api()
        processor.dispatch_messages(s)


if __name__ == '__main__':
    main()
