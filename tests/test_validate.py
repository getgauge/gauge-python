import unittest

from getgauge.validator import random_word, is_valid, format_params


class ValidateTests(unittest.TestCase):
    def test_random_word(self):
        self.assertNotEqual(random_word(), random_word())

    def test_is_valid(self):
        self.assertTrue(is_valid("param", "{} = None"))
        self.assertTrue(is_valid("_param_", "{} = None"))

        self.assertFalse(is_valid(".$_", "{} = None"))
        self.assertFalse(is_valid("2", "{} = None"))

    def test_format_params(self):
        self.assertEqual("a, b, arg3", format_params(["a", "b", "2"]))
