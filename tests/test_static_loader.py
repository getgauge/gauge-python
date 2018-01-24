import unittest

from getgauge.registry import registry
from getgauge.static_loader import load_file


class StaticLoaderTests(unittest.TestCase):
    def setUp(self):
        registry.clear()

    def test_loader_populates_registry_from_given_file_content(self):
        content = """
        @step("print hello")
        def print():
            print("hello")


        @step("print <hello>.")
        def print_word(word):
            print(word)

        """
        load_file(content, "foo.py")
        self.assertTrue(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print {}."))
        self.assertEqual(len(registry.steps()), 2)

    def test_loader_populates_registry_with_duplicate_steps(self):
        content = """
        @step("print hello")
        def print():
            print("hello")


        @step("print hello")
        def print_word():
            print("hello")

        """
        load_file(content, "foo.py")
        self.assertTrue(registry.has_multiple_impls("print hello"))

    def test_loader_does_not_populate_registry_for_content_having_parse_error(self):
        content = """
        @step("print hello")
        def print():
            print(.__str_())

        """
        load_file(content, "foo.py")
        self.assertFalse(registry.is_implemented("print hello"))

    def test_loader_populates_registry_for_with_aliases(self):
        content = """
        @step(["print hello", "say hello"])
        def print():
            print("hello")

        """
        load_file(content, "foo.py")
        self.assertTrue(registry.is_implemented("say hello"))
        self.assertTrue(registry.get_info_for("say hello").has_alias)

    def tearDown(self):
        registry.clear()


if __name__ == '__main__':
    unittest.main()
