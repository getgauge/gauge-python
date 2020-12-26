import sys
import unittest
from textwrap import dedent
from getgauge.parser import Parser


def _span(start, startChar, end, endChar):
    return locals()


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.preservesNewlines = False

    def parse(self, content, file_path='foo.py'):
        return Parser.parse(file_path, content)
    
    def assertSpanStart(self, actualSpan, expectedStartLine, expectedStartChar):
        if callable(actualSpan):
            actualSpan = actualSpan()
        self.assertEqual(actualSpan['start'], expectedStartLine)
        self.assertEqual(actualSpan['startChar'], expectedStartChar)

    def test_can_parse_content_directly(self):
        content = dedent('''\
        class test:
            @step("print hello")
            def print_hello():
                print("hello")

            @step('print <hello>.')
            def print_word(word):
                print(word)

        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        self.assertEqual(pf.get_code(), content)

    def test_does_not_parse_invalid_code(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello)
        ''')
        pf = self.parse(content)
        self.assertIsNone(pf)

    def test_can_parse_chinese_content_directly(self):
        content = dedent('''\
        class test:
            @step("打印你好")
            def print_hello():
                print("hello")

            @step('打印 <hello>.')
            def print_word(word):
                print(word)

        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        self.assertEqual(pf.get_code(), content)

    def test_iter_steps_loads_steps_from_content(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello")

        @step("print <word>")
        def print_word(word):
            print(word)
        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0][0], "print hello")
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)
        self.assertEqual(steps[1][0], "print <word>")
        self.assertEqual(steps[1][1], "print_word")
        self.assertSpanStart(steps[1][2], 5, 0)

    def test_iter_steps_loads_multiple_steps_from_list(self):
        content = dedent('''\
        @step(["print hello", "display hello"])
        def print_hello():
            print("hello")

        @step([
            "print <word>",
            'display <word>',
        ])
        def print_word(word):
            print(word)
        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0][0], ["print hello", "display hello"])
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)
        self.assertEqual(steps[1][0], ["print <word>", "display <word>"])
        self.assertEqual(steps[1][1], "print_word")
        self.assertSpanStart(steps[1][2], 5, 0)

    def test_iter_steps_only_checks_step_decorator(self):
        content = dedent('''\
        @step("print <word>")
        @Step("hello")
        def print_word(word):
            print(word)

        @_step("print <word>")
        def print_words(word):
            print(word)
        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0][0], "print <word>")
        self.assertEqual(steps[0][1], "print_word")
        self.assertSpanStart(steps[0][2], 1, 0)

    def test_iter_steps_loads_multiple_step_implementations(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello")

        @step("print hello")
        def print_word(word):
            print(word)
        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0][0], "print hello")
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)
        self.assertEqual(steps[1][0], "print hello")
        self.assertEqual(steps[1][1], "print_word")
        self.assertSpanStart(steps[1][2], 5, 0)

    def test_iter_steps_loads_triple_quoted_strings_1(self):
        content = dedent('''\
        @step("""print hello""")
        def print_hello():
            print("hello")
        ''')
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0][0], "print hello")
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)

    def test_iter_steps_loads_triple_quoted_strings_2(self):
        content = dedent("""\
        @step('''print hello''')
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0][0], "print hello")
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)

    def test_iter_steps_loads_r_strings(self):
        content = dedent("""\
        @step(r'''print hello''')
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0][0], "print hello")
        self.assertEqual(steps[0][1], "print_hello")
        self.assertSpanStart(steps[0][2], 1, 0)

    @unittest.skipIf(sys.hexversion < 0x3060000, "f-strings are introduced in python3.6")
    def test_iter_steps_does_not_load_f_strings(self):
        content = dedent("""\
        @step(f'print hello')
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 0)

    def test_iter_steps_does_not_load_indirect_args(self):
        content = dedent("""\
        s = 'print hello'

        @step(s)
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 0)

    def test_iter_steps_does_not_load_non_string_arg(self):
        content = dedent("""\
        @step(100)
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 0)

    def test_refactor_step_only_step_text(self):
        content = dedent("""\
        @step("print hello")
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print hello', 'display hello', [])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 19), '"display hello"'),
        ])
        self.assertEqual(pf.get_code(), content.replace(
            'print hello', 'display hello'))

    def test_refactor_step_only_step_text_in_list(self):
        content = dedent("""\
        @step([
            "print <word>",
            'display <word>',
        ])
        def print_word(word):
            print(word)
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('display <word>', 'show <word>', [0])
        self.assertEqual(diffs, [
            (_span(3, 4, 3, 20), "'show <word>'"),
        ])
        self.assertEqual(pf.get_code(), content.replace(
            'display <word>', 'show <word>'))

    def test_refactor_step_add_arg_in_empty(self):
        content = dedent("""\
        @step('print hello')
        def print_hello():
            print("hello")
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print hello', 'print <word>', [-1])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 19), "'print <word>'"),
            (_span(2, 16, 2, 16), "arg0"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step('print <word>')
        def print_hello(arg0):
            print("hello")
        """))

    def test_refactor_step_add_arg_at_start(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [-1, 0, 1, 2])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (_span(2, 8, 2, 15), "arg0, a, b, z"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul(arg0, a, b, z):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_at_end(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <b>, <x> equals <z>',
            [0, 1, 2, -1])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <a>, <b>, <x> equals <z>"'),
            (_span(2, 8, 2, 15), "a, b, z, arg3"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b>, <x> equals <z>")
        def mul(a, b, z, arg3):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_in_middle(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <b>, <x> equals <z>',
            [0, 1, -1, 2])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <a>, <b>, <x> equals <z>"'),
            (_span(2, 8, 2, 15), "a, b, arg2, z"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b>, <x> equals <z>")
        def mul(a, b, arg2, z):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_at_start_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a,
                b,
                z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [-1, 0, 1, 2])

        expectedArgs = "arg0,\n        a,\n        b,\n        z"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (_span(2, 8, 4, 9), expectedArgs),
        ])

        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul({}):
            assert z == a * b
        """).format(expectedArgs))

    def test_refactor_step_add_arg_at_end_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a,
                b,
                z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [0, 1, 2, -1])

        expectedArgs = "a,\n        b,\n        z,\n        arg3"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (_span(2, 8, 4, 9), expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul({}):
            assert z == a * b
        """).format(expectedArgs))

    def test_refactor_step_add_arg_in_middle_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a,
                b,
                z):
            assert z == a * b
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <x>, <b> equals <z>',
            [0, -1, 1, 2])

        expectedArgs = "a,\n        arg1,\n        b,\n        z"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <a>, <x>, <b> equals <z>"'),
            (_span(2, 8, 4, 9), expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <x>, <b> equals <z>")
        def mul({}):
            assert z == a * b
        """).format(expectedArgs))

    def test_refactor_step_remove_only_arg(self):
        content = dedent("""\
        @step("print <word>")
        def print_word(word):
            print(word)
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print <word>', 'print hello', [])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 20), '"print hello"'),
            (_span(2, 15, 2, 19), ""),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("print hello")
        def print_word():
            print(word)
        """))

    def test_refactor_step_remove_first_arg(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a, b, c, z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <b>, <c> equals <z>',
            [1, 2, 3])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <b>, <c> equals <z>"'),
            (_span(2, 8, 2, 18), "b, c, z"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <b>, <c> equals <z>")
        def mul(b, c, z):
            assert z == a * b * c
        """))

    def test_refactor_step_remove_last_arg(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a, b, c, z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <c>',
            [0, 1, 2])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <a>, <b> equals <c>"'),
            (_span(2, 8, 2, 18), "a, b, c"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b> equals <c>")
        def mul(a, b, c):
            assert z == a * b * c
        """))

    def test_refactor_step_remove_arg_in_middle(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a, b, c, z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <z>',
            [0, 1, 3])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <a>, <b> equals <z>"'),
            (_span(2, 8, 2, 18), "a, b, z"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b * c
        """))
        # Remove one more arg
        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a> equals <z>',
            [0, 2])
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <a> equals <z>"'),
            (_span(2, 8, 2, 15), "a, z"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a> equals <z>")
        def mul(a, z):
            assert z == a * b * c
        """))

    def test_refactor_step_remove_first_arg_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a,
                b,
                c,
                z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <b>, <c> equals <z>',
            [1, 2, 3])

        expectedArgs = "b,\n        c,\n        z"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <b>, <c> equals <z>"'),
            (_span(2, 8, 5, 9), expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <b>, <c> equals <z>")
        def mul({}):
            assert z == a * b * c
        """).format(expectedArgs))

    def test_refactor_step_remove_last_arg_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a,
                b,
                c,
                z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <c>',
            [0, 1, 2])

        expectedArgs = "a,\n        b,\n        c"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <a>, <b> equals <c>"'),
            (_span(2, 8, 5, 9), expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b> equals <c>")
        def mul({}):
            assert z == a * b * c
        """).format(expectedArgs))

    def test_refactor_step_remove_arg_in_middle_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b>, <c> equals <z>")
        def mul(a,
                b,
                c,
                z):
            assert z == a * b * c
        """)
        pf = self.parse(content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <z>',
            [0, 1, 3])

        expectedArgs = "a,\n        b,\n        z"
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 41), '"multiply <a>, <b> equals <z>"'),
            (_span(2, 8, 5, 9), expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul({}):
            assert z == a * b * c
        """).format(expectedArgs))

        # Remove one more arg
        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a> equals <z>',
            [0, 2])
        expectedArgs = "a,\n        z"
        expectedArgSpan = _span(2, 8, 2, 31)
        if not self.preservesNewlines:
            expectedArgs = expectedArgs.replace('\n       ', '')
            expectedArgSpan = _span(2, 8, 2, 15)
        self.assertEqual(diffs, [
            (_span(1, 6, 1, 36), '"multiply <a> equals <z>"'),
            (expectedArgSpan, expectedArgs),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a> equals <z>")
        def mul({}):
            assert z == a * b * c
        """).format(expectedArgs))


if __name__ == '__main__':
    unittest.main()
