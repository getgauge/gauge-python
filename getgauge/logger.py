import logging
from logging.handlers import RotatingFileHandler
import os
import configparser
import util



def get_logger(name):
    config = _read_config()
    logger = logging.getLogger(name)
    logger.propagate = False
    level = config.get('LOGGING','runner_log_level')
    logger.setLevel(level)
    file_name = _create_log_file(config)
    handler = RotatingFileHandler(file_name, maxBytes=config.get('LOGGING','log_file_max_size'),
                                  backupCount=config.get('LOGGING','log_file_backup_count'))
    handler.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] {%(module)s:%(funcName)s:%(lineno)d} - %(message)s','%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def _create_log_file(config):
    dir_path = os.path.join(util.get_project_root(), 'logs')
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = dir_path + config.get('LOGGING','log_file_name')
    return file_name

def _read_config():
    config = configparser.RawConfigParser()
    config.read(os.path.join(util.get_project_root(), 'env/default/python.properties'))
    return config
