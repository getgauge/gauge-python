import os
import unittest
from pathlib import Path

from getgauge.impl_loader import load_impls
from getgauge.registry import registry


class ImplLoaderTest(unittest.TestCase):

    def test_update_step_registry_with_class(self):

        tests_directory = str(Path(__file__).resolve().parent)
        relative_file_path = os.path.join('..', 'test_relative_import')

        load_impls(
            step_impl_dirs=[relative_file_path],
            project_root=tests_directory
        )

        loaded_steps = registry.get_steps_map()

        self.assertEqual(2, len(loaded_steps))

        step_infos_of_class_instance = loaded_steps["Greet {} from inside the class"]

        self.assertEqual(1, len(step_infos_of_class_instance))
        self.assertIsNotNone(step_infos_of_class_instance[0].instance)

        self.assertEqual(
            ["Greet <name> from inside the class", "Greet <name> from outside the class"],
            registry.steps()
        )

    def test_update_step_registry_with_class_one_level_above(self):

        repo_root_directory = str(Path(__file__).resolve().parent.parent)
        relative_file_path_one_level_above = os.path.join('tests', '..', 'test_relative_import')

        load_impls(
            step_impl_dirs=[relative_file_path_one_level_above],
            project_root=repo_root_directory
        )

        loaded_steps = registry.get_steps_map()

        self.assertEqual(2, len(loaded_steps))

        step_infos_of_class_instance = loaded_steps["Greet {} from inside the class"]

        self.assertEqual(1, len(step_infos_of_class_instance))
        self.assertIsNotNone(step_infos_of_class_instance[0].instance)

        self.assertEqual(
            ["Greet <name> from inside the class", "Greet <name> from outside the class"],
            registry.steps()
        )


if __name__ == '__main__':
    unittest.main()
