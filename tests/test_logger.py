from pyfakefs.fake_filesystem_unittest import TestCase
from unittest import main
import getgauge
import configparser
import os
import logging

config = configparser.RawConfigParser()
config.read(os.path.join(getgauge.util.get_project_root(), 'env/default/python.properties'))

class LoggerTests(TestCase):

    def test_get_logger(self):
        logger = getgauge.logger.get_logger('test')
        self.assertEqual(logger.name,'test')
        self.assertFalse(logger.propagate)
        self.assertEqual(logging.getLevelName(logger.getEffectiveLevel()),config.get('LOGGING','runner_log_level'))
        self.assertIn('/logs/runner.log',logger.handlers[0].baseFilename)


if __name__ == '__main__':
    main()        