import six
import unittest
from textwrap import dedent
from getgauge.parser import PythonFile, Span


class ParserPythonFileTests(unittest.TestCase):
    def test_can_parse_content_directly(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello")

        @step('print <hello>.')
        def print_word(word):
            print(word)

        ''')
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        self.assertEqual(pf.get_code(), content)

    def test_does_not_parse_invalid_code(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello)
        ''')
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNone(pf)

    def test_iter_steps_loads_steps_from_content(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello")

        @step("print <word>")
        def print_word(word):
            print(word)
        ''')
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].steps, "print hello")
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))
        self.assertEqual(steps[1].steps, "print <word>")
        self.assertEqual(steps[1].func.name.value, "print_word")
        self.assertEqual(steps[1].span, Span(6, 0, 8, 0))

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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].steps, ["print hello", "display hello"])
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))
        self.assertEqual(steps[1].steps, ["print <word>", "display <word>"])
        self.assertEqual(steps[1].func.name.value, "print_word")
        self.assertEqual(steps[1].span, Span(9, 0, 11, 0))

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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].steps, "print <word>")
        self.assertEqual(steps[0].func.name.value, "print_word")
        self.assertEqual(steps[0].span, Span(3, 0, 5, 0))

    def test_iter_steps_loads_multiple_step_implementations(self):
        content = dedent('''\
        @step("print hello")
        def print_hello():
            print("hello")

        @step("print hello")
        def print_word(word):
            print(word)
        ''')
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].steps, "print hello")
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))
        self.assertEqual(steps[1].steps, "print hello")
        self.assertEqual(steps[1].func.name.value, "print_word")
        self.assertEqual(steps[1].span, Span(6, 0, 8, 0))

    def test_iter_steps_loads_triple_quoted_strings_1(self):
        content = dedent('''\
        @step("""print hello""")
        def print_hello():
            print("hello")
        ''')
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].steps, "print hello")
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))

    def test_iter_steps_loads_triple_quoted_strings_2(self):
        content = dedent("""\
        @step('''print hello''')
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].steps, "print hello")
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))

    def test_iter_steps_loads_r_strings(self):
        content = dedent("""\
        @step(r'''print hello''')
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].steps, "print hello")
        self.assertEqual(steps[0].func.name.value, "print_hello")
        self.assertEqual(steps[0].span, Span(2, 0, 4, 0))

    @unittest.skipIf(six.PY2, "f-strings are not supported on python2")
    def test_iter_steps_does_not_load_f_strings(self):
        content = dedent("""\
        @step(f'print hello')
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 0)

    def test_iter_steps_does_not_load_non_string_arg(self):
        content = dedent("""\
        @step(100)
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        steps = list(pf.iter_steps())
        self.assertEqual(len(steps), 0)

    def test_find_step_node_can_find_step(self):
        content = dedent("""\
        @step('print hello')
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)
        step, func = pf._find_step_node('print hello')
        self.assertEqual(step.start_pos, (1, 6))
        self.assertEqual(func.name.value, 'print_hello')

    def test_find_step_node_can_find_step_within_multiple(self):
        content = dedent("""\
        @step(["print hello", "display hello"])
        def print_hello():
            print("hello")

        @step([
            "print <word>",
            'display <word>',
        ])
        def print_word(word):
            print(word)
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        step, func = pf._find_step_node('display hello')
        self.assertEqual(step.start_pos, (1, 22))
        self.assertEqual(func.name.value, 'print_hello')

        step, func = pf._find_step_node('display <word>')
        self.assertEqual(step.start_pos, (7, 4))
        self.assertEqual(func.name.value, 'print_word')

    def test_refactor_step_only_step_text(self):
        content = dedent("""\
        @step("print hello")
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print hello', 'display hello', [])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 19), '"display hello"'),
        ])
        self.assertEqual(pf.get_code(), content.replace('print hello', 'display hello'))

    def test_refactor_step_only_step_text_in_list(self):
        content = dedent("""\
        @step([
            "print <word>",
            'display <word>',
        ])
        def print_word(word):
            print(word)
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('display <word>', 'show <word>', [0])
        self.assertEqual(diffs, [
            (Span(3, 4, 3, 20), "'show <word>'"),
        ])
        self.assertEqual(pf.get_code(), content.replace('display <word>', 'show <word>'))

    def test_refactor_step_add_arg_in_empty(self):
        content = dedent("""\
        @step('print hello')
        def print_hello():
            print("hello")
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print hello', 'print <word>', [-1])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 19), "'print <word>'"),
            (Span(2, 15, 2, 17), "(arg1)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step('print <word>')
        def print_hello(arg1):
            print("hello")
        """))

    def test_refactor_step_add_arg_at_start(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [-1, 0, 1, 2])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (Span(2, 7, 2, 16), "(arg1, a, b, z)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul(arg1, a, b, z):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_at_end(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <b>, <x> equals <z>',
            [0, 1, 2, -1])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <a>, <b>, <x> equals <z>"'),
            (Span(2, 7, 2, 16), "(a, b, z, arg4)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b>, <x> equals <z>")
        def mul(a, b, z, arg4):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_in_middle(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a, b, z):
            assert z == a * b
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <b>, <x> equals <z>',
            [0, 1, -1, 2])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <a>, <b>, <x> equals <z>"'),
            (Span(2, 7, 2, 16), "(a, b, arg3, z)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <b>, <x> equals <z>")
        def mul(a, b, arg3, z):
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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [-1, 0, 1, 2])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (Span(2, 7, 4, 10), "(arg1,\n        a,\n        b,\n        z)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul(arg1,
                a,
                b,
                z):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_at_end_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a,
                b,
                z):
            assert z == a * b
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <x>, <a>, <b> equals <z>',
            [0, 1, 2, -1])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <x>, <a>, <b> equals <z>"'),
            (Span(2, 7, 4, 10), "(a,\n        b,\n        z,\n        arg4)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <x>, <a>, <b> equals <z>")
        def mul(a,
                b,
                z,
                arg4):
            assert z == a * b
        """))

    def test_refactor_step_add_arg_in_middle_newline(self):
        content = dedent("""\
        @step("multiply <a>, <b> equals <z>")
        def mul(a,
                b,
                z):
            assert z == a * b
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b> equals <z>',
            'multiply <a>, <x>, <b> equals <z>',
            [0, -1, 1, 2])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 36), '"multiply <a>, <x>, <b> equals <z>"'),
            (Span(2, 7, 4, 10), "(a,\n        arg2,\n        b,\n        z)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a>, <x>, <b> equals <z>")
        def mul(a,
                arg2,
                b,
                z):
            assert z == a * b
        """))

    def test_refactor_step_remove_only_arg(self):
        content = dedent("""\
        @step("print <word>")
        def print_word(word):
            print(word)
        """)
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step('print <word>', 'print hello', [])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 20), '"print hello"'),
            (Span(2, 14, 2, 20), "()"),
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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <b>, <c> equals <z>',
            [1, 2, 3])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 41), '"multiply <b>, <c> equals <z>"'),
            (Span(2, 7, 2, 19), "(b, c, z)"),
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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <c>',
            [0, 1, 2])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 41), '"multiply <a>, <b> equals <c>"'),
            (Span(2, 7, 2, 19), "(a, b, c)"),
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
        pf = PythonFile.parse('foo.py', content)
        self.assertIsNotNone(pf)

        diffs = pf.refactor_step(
            'multiply <a>, <b>, <c> equals <z>',
            'multiply <a>, <b> equals <z>',
            [0, 1, 3])
        self.assertEqual(diffs, [
            (Span(1, 6, 1, 41), '"multiply <a>, <b> equals <z>"'),
            (Span(2, 7, 2, 19), "(a, b, z)"),
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
            (Span(1, 6, 1, 36), '"multiply <a> equals <z>"'),
            (Span(2, 7, 2, 16), "(a, z)"),
        ])
        self.assertEqual(pf.get_code(), dedent("""\
        @step("multiply <a> equals <z>")
        def mul(a, z):
            assert z == a * b * c
        """))