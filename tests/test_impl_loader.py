import os
import unittest

from getgauge.impl_loader import update_step_registry_with_class
from test_relative_import.relative_import_class import Sample


class ImplLoaderTest(unittest.TestCase):
    def setUp(self):
        self.curr_dir = os.getcwd()
        self.relative_file_path = os.path.join('..', 'test_relative_import', 'relative_import_class.py')
        self.relative_file_path_one_level_above = os.path.join('tests', '..', 'test_relative_import', 'relative_import_class.py')

    def test_update_step_registry_with_class(self):
        os.chdir('tests')
        method_list = update_step_registry_with_class(Sample(), self.relative_file_path)
        os.chdir(self.curr_dir)
        self.assertEqual(["Greet <name> from inside the class", 
                          "Greet <name> from outside the class"], 
                          [method.step_text for method in method_list])

    def test_update_step_registry_with_class_one_level_above(self):
        os.chdir(self.curr_dir)
        method_list = update_step_registry_with_class(Sample(), self.relative_file_path_one_level_above)
        self.assertEqual(["Greet <name> from inside the class", 
                          "Greet <name> from outside the class"], 
                          [method.step_text for method in method_list])


if __name__ == '__main__':
    unittest.main()
