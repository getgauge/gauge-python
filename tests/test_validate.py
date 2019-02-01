import unittest

from getgauge.validator import _random_word, _is_valid, _format_params


class ValidateTests(unittest.TestCase):
    def test_random_word(self):
        self.assertNotEqual(_random_word(), _random_word())

    def test_is_valid(self):
        self.assertTrue(_is_valid("param", "{} = None"))
        self.assertTrue(_is_valid("_param_"))

        self.assertFalse(_is_valid(".$_", "{} = None"))
        self.assertFalse(_is_valid("2", "{} = None"))

    def test_format_params(self):
        self.assertEqual("a, b, arg3", _format_params(["a", "b", "2"]))

if __name__ == '__main__':
    unittest.main()        
