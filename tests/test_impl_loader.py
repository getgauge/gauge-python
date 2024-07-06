import os
import unittest

from test_relative_import.relative_import_class import Sample
from getgauge.impl_loader import update_step_registry_with_class


class ImplLoaderTest(unittest.TestCase):
    def setUp(self):
        self.relative_file_path = os.path.join('..', 'test_relative_import', 'relative_import_class.py')

    def test_update_step_resgistry_with_class(self):
        curr_dir = os.getcwd()
        os.chdir('tests')
        method_list = update_step_registry_with_class(Sample(), self.relative_file_path)
        os.chdir(curr_dir)
        self.assertEqual(["Greet <name> from inside the class", 
                          "Greet <name> from outside the class"], 
                          [method.step_text for method in method_list])

    
if __name__ == '__main__':
    unittest.main()
