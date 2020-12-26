import sys
import unittest
from textwrap import dedent
from getgauge.registry import registry
from getgauge.parser import Parser
from getgauge.static_loader import load_steps, reload_steps


class StaticLoaderTests(unittest.TestCase):
    def setUp(self):
        registry.clear()

    def test_loader_populates_registry_from_given_file_content(self):
        content = dedent("""
        @step("print hello")
        def printf():
            print("hello")


        @step("print <hello>.")
        def print_word(word):
            print(word)

        """)
        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print {}."))
        self.assertEqual(len(registry.steps()), 2)

    def test_loader_populates_registry_only_with_steps_from_given_file_content(self):
        content = dedent("""
        @step("print hello")
        def printf():
            print("hello")


        @hello("some other decorator")
        @step("print <hello>.")
        def print_word(word):
            print(word)

        """)
        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print {}."))
        self.assertFalse(registry.is_implemented("some other decorator"))

    def test_loader_populates_registry_with_duplicate_steps(self):
        content = dedent("""
        @step("print hello")
        def printf():
            print("hello")


        @step("print hello")
        def print_word():
            print("hello")

        """)
        load_steps(Parser.parse("foo.py", content))
        self.assertTrue(registry.has_multiple_impls("print hello"))

    def test_loader_populates_registry_for_with_aliases(self):
        content = dedent("""
        @step(["print hello", "say hello"])
        def printf():
            print("hello")

        """)

        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("say hello"))
        self.assertTrue(registry.get_info_for("say hello").has_alias)

    def test_loader_reload_registry_for_given_content(self):
        content = dedent("""
            @step("print hello")
            def printf():
                print("hello")
            """)
        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("print hello"))

        content = dedent("""
                @step("print world")
                def printf():
                    print("hello")
                """)

        reload_steps('foo.py', content)

        self.assertFalse(registry.is_implemented("print hello"))
        self.assertTrue(registry.is_implemented("print world"))

    def test_loader_reload_registry_for_given_content_with_empty_arg(self):
        content = dedent("""
            @step("print hello <>")
            def printf(arg1):
                print(arg1)
            """)
        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("print hello {}"))

    def test_loader_triple_quote_strings(self):
        content = dedent("""
            @step('''print hello <>''')
            def printf(arg1):
                print(arg1)
            """)
        load_steps(Parser.parse("foo.py", content))

        self.assertTrue(registry.is_implemented("print hello {}"))

    def test_loader_step_indirect_argument(self):
        content = dedent("""
            v = 'print hello <>'
            @step(v)
            def printf(arg1):
                print(arg1)
            """)
        load_steps(Parser.parse("foo.py", content))

        self.assertFalse(registry.is_implemented("print hello {}"))

    def test_loader_non_string_argument(self):
        content = dedent("""
            @step(100)
            def printf(arg1):
                print(arg1)
            """)
        load_steps(Parser.parse("foo.py", content))

        self.assertFalse(registry.is_implemented("print hello {}"))

    def tearDown(self):
        registry.clear()


if __name__ == '__main__':
    unittest.main()
