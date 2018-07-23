import unittest

from getgauge.registry import registry
from getgauge.static_loader import load_steps, reload_steps, generate_ast


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
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print {}."))
        self.assertEqual(len(registry.steps()), 2)

    def test_loader_populates_registry_only_with_steps_from_given_file_content(self):
        content = """
        @step("print hello")
        def print():
            print("hello")


        @hello("some other decorator")
        @step("print <hello>.")
        def print_word(word):
            print(word)

        """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print {}."))
        self.assertFalse(registry.is_implemented("some other decorator"))

    def test_loader_populates_registry_with_duplicate_steps(self):
        content = """
        @step("print hello")
        def print():
            print("hello")


        @step("print hello")
        def print_word():
            print("hello")

        """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")
        self.assertTrue(registry.has_multiple_impls("print hello"))

    def test_loader_does_not_populate_registry_for_content_having_parse_error(self):
        content = """
        @step("print hello")
        def print():
            print(.__str_())

        """
        ast = generate_ast(content, "foo.py")
        if ast:
            load_steps(ast, "foo.py")

        self.assertFalse(registry.is_implemented("print hello"))

    def test_loader_populates_registry_for_with_aliases(self):
        content = """
        @step(["print hello", "say hello"])
        def print():
            print("hello")

        """

        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("say hello"))
        self.assertTrue(registry.get_info_for("say hello").has_alias)

    def test_loader_reload_registry_for_given_content(self):
        content = """
            @step("print hello")
            def print():
                print("hello")
            """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("print hello"))

        content = """
                @step("print world")
                def print():
                    print("hello")
                """

        reload_steps(content, 'foo.py')

        self.assertFalse(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print world"))

    def test_loader_reload_registry_for_given_content_with_empty_arg(self):
        content = """
            @step("print hello <>")
            def print(arg1):
                print(arg1)
            """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("print hello {}"))

    def test_loader_triple_quote_strings(self):
        content = """
            @step('''print hello <>''')
            def print(arg1):
                print(arg1)
            """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertTrue(registry.is_implemented("print hello {}"))

    def test_loader_step_indirect_argument(self):
        content = """
            v = 'print hello <>'
            @step(v)
            def print(arg1):
                print(arg1)
            """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertFalse(registry.is_implemented("print hello {}"))

    def test_loader_non_string_argument(self):
        content = """
            @step(100)
            def print(arg1):
                print(arg1)
            """
        ast = generate_ast(content, "foo.py")
        load_steps(ast, "foo.py")

        self.assertFalse(registry.is_implemented("print hello {}"))


def tearDown(self):
    registry.clear()


if __name__ == '__main__':
    unittest.main()
