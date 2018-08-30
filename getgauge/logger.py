import logging
import os
import sys



def get_logger():
    if os.getenv('IS_DAEMON'):
        f = '%(asctime)s.%(msecs)03d %(message)s'
        logging.basicConfig(stream=sys.stdout, format=f, level=logging.DEBUG, datefmt='%H:%M:%S')
    else:
        logging.basicConfig(stream=sys.stdout, format='%(message)s', level=logging.DEBUG)
    return logging.getLogger() 


logger = get_logger()


def except_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception",exc_info=(exc_type, exc_value, exc_traceback))

# Install exception handler
sys.excepthook = except_handler
    
