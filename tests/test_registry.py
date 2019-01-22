import re
import unittest

from getgauge.registry import Registry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        global registry
        registry = Registry()

    def test_Registry_add_step_definition(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func'},
                 {'text': 'Step 1', 'func': 'func1'}]

        for info in infos:
            registry.add_step(info['text'], info['func'], '')

        self.assertEqual([info['text'] for info in infos].sort(),
                         registry.steps().sort())

        for info in infos:
            parsed_step_text = re.sub('<[^<]+?>', '{}', info['text'])
            self.assertEqual(info['func'],
                             registry.get_info_for(parsed_step_text).impl)

    def test_Registry_add_step_definition_with_continue_on_failure(self):
        registry.add_step('Step 1', 'func', '')
        registry.continue_on_failure('func', [RuntimeError])

        self.assertEqual(True,
                         registry.is_continue_on_failure('func',
                                                         RuntimeError()))

    def test_Registry_add_step_definition_with_continue_on_failure_for_different_exceptions(self):
        registry.add_step('Step 1', 'func', '')
        registry.continue_on_failure('func', [RuntimeError])

        self.assertEqual(False,
                         registry.is_continue_on_failure('func', IndexError()))

    def test_Registry_add_step_definition_with_parent_class_continue_on_failure(self):
        registry.add_step('Step 1', 'func', '')
        registry.continue_on_failure('func', [Exception])

        self.assertEqual(True,
                         registry.is_continue_on_failure('func',
                                                         RuntimeError()))

    def test_Registry_add_step_definition_with_alias(self):
        registry.add_step(['Say <hello> to <getgauge>.',
                           'Tell <hello> to <getgauge>.'], 'impl', '')

        info1 = registry.get_info_for('Say {} to {}.')
        info2 = registry.get_info_for('Tell {} to {}.')

        self.assertEqual(info1.has_alias, True)
        self.assertEqual(info2.has_alias, True)

    def test_Registry_get_step_info(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func'},
                 {'text': 'Step 1', 'func': 'func1'}]

        for info in infos:
            registry.add_step(info['text'], info['func'], '')

        self.assertEqual('Say <hello> to <getgauge>',
                         registry.get_info_for('Say {} to {}').step_text)

        self.assertEqual('Say {} to {}',
                         registry.get_info_for('Say {} to {}').parsed_step_text)

        self.assertEqual('Step 1', registry.get_info_for('Step 1').step_text)

        self.assertEqual(None, registry.get_info_for('Step21').step_text)

    def test_Registry_is_step_implemented(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func'},
                 {'text': 'Step 1', 'func': 'func1'}]

        for info in infos:
            registry.add_step(info['text'], info['func'], '')

        for info in infos:
            parsed_step_text = re.sub('<[^<]+?>', '{}', info['text'])
            self.assertTrue(registry.is_implemented(parsed_step_text))

    def test_Registry_has_multiple_impls(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func'},
                 {'text': 'Say <hello> to <getgauge>', 'func': 'func'},
                 {'text': 'Step 1', 'func': 'func1'}]
        for info in infos:
            registry.add_step(info['text'], info['func'], '')

        parsed_step_text = re.sub('<[^<]+?>', '{}', infos[0]['text'])

        self.assertTrue(registry.has_multiple_impls(parsed_step_text))
        self.assertFalse(registry.has_multiple_impls(infos[2]['text']))

    def test_Registry_get_multiple_impls(self):
        infos = [{'text': 'Say <hello> to <getgauge>',
                  'func': 'func', 'line': 1},
                 {'text': 'Say <hello> to <getgauge>',
                  'func': 'func', 'line': 2},
                 {'text': 'Step 1', 'func': 'func1', 'line': 3}]

        for info in infos:
            registry.add_step(info['text'], info['func'],
                              '', {'start': info['line']})

        parsed_step_text = re.sub('<[^<]+?>', '{}', infos[0]['text'])

        self.assertTrue(registry.has_multiple_impls(parsed_step_text))
        self.assertEqual(
            set([info.span['start']
                 for info in registry.get_infos_for(parsed_step_text)]),
            {infos[0]['line'], infos[1]['line']})

        self.assertEqual(
            set([info.step_text
                 for info in registry.get_infos_for(parsed_step_text)]),
            {infos[0]['text'], infos[1]['text']})

    def test_Registry_before_suite(self):
        infos = ['before suite func', 'before suite func1']
        for info in infos:
            registry.add_before_suite(info)

        self.assertEqual(infos, [i.impl for i in registry.before_suite()])

    def test_Registry_after_suite(self):
        infos = ['after suite func', 'after suite func1']
        for info in infos:
            registry.add_after_suite(info)

        self.assertEqual(infos, [i.impl for i in registry.after_suite()])

    def test_Registry_before_spec(self):
        infos = ['before spec func', 'before spec func1']
        for info in infos:
            registry.add_before_spec(info)

        self.assertEqual(infos, [i.impl for i in registry.before_spec()])

    def test_Registry_after_spec(self):
        infos = ['after spec func', 'after spec func1']
        for info in infos:
            registry.add_after_spec(info)

        self.assertEqual(infos, [i.impl for i in registry.after_spec()])

    def test_Registry_before_spec_with_tags(self):
        info1 = {'tags': None, 'func': 'before spec func'}
        info2 = {'tags': '<A> and <b> and not <c>',
                 'func': 'before spec func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'before spec func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_before_spec(info['func'], info['tags'])

        self.assertEqual([info1['func']], [i.impl for i in registry.before_spec([])])
        self.assertEqual([x['func'] for x in infos], [i.impl for i in registry.before_spec(['A', 'b'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.before_spec(['A', 'b', 'c'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.before_spec(['A'])])
        self.assertEqual([info1['func']], [i.impl for i in registry.before_spec(['A', 'c'])])

    def test_Registry_after_spec_with_tags(self):
        info1 = {'tags': None, 'func': 'after spec func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'after spec func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'after spec func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_after_spec(info['func'], info['tags'])

        self.assertEqual([info1['func']], [i.impl for i in registry.after_spec([])])
        self.assertEqual([x['func'] for x in infos], [i.impl for i in registry.after_spec(['A', 'b'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.after_spec(['A', 'b', 'c'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.after_spec(['A'])])
        self.assertEqual([info1['func']], [i.impl for i in registry.after_spec(['A', 'c'])])

    def test_Registry_before_scenario(self):
        infos = ['before scenario func', 'before scenario func1']
        for info in infos:
            registry.add_before_scenario(info)

        self.assertEqual(infos, [i.impl for i in registry.before_scenario()])

    def test_Registry_after_scenario(self):
        infos = ['after scenario func', 'after scenario func1']
        for info in infos:
            registry.add_after_scenario(info)

        self.assertEqual(infos, [i.impl for i in registry.after_scenario()])

    def test_Registry_before_scenario_with_tags(self):
        info1 = {'tags': None, 'func': 'before scenario func'}
        info2 = {'tags': '<A> and <b> and not <c>',
                 'func': 'before scenario func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'before scenario func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_before_scenario(info['func'], info['tags'])

        self.assertEqual([info1['func']],
                         [i.impl for i in registry.before_scenario([])])

        self.assertEqual([x['func'] for x in infos],
                         [i.impl for i in registry.before_scenario(['A', 'b'])])

        self.assertEqual([info1['func'], info3['func']],
                         [i.impl for i in registry.before_scenario(['A', 'b', 'c'])])

        self.assertEqual([info1['func'], info3['func']],
                         [i.impl for i in registry.before_scenario(['A'])])

        self.assertEqual([info1['func']], [i.impl for i in registry.before_scenario(['A', 'c'])])

    def test_Registry_after_scenario_with_tags(self):
        info1 = {'tags': None, 'func': 'after scenario func'}
        info2 = {'tags': '<A> and <b> and not <c>',
                 'func': 'after scenario func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'after scenario func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_after_scenario(info['func'], info['tags'])

        self.assertEqual([info1['func']], [i.impl for i in registry.after_scenario([])])
        self.assertEqual([x['func'] for x in infos],
                         [i.impl for i in registry.after_scenario(['A', 'b'])])

        self.assertEqual([info1['func'], info3['func']],
                         [i.impl for i in registry.after_scenario(['A', 'b', 'c'])])

        self.assertEqual([info1['func'], info3['func']],
                         [i.impl for i in registry.after_scenario(['A'])])

        self.assertEqual([info1['func']], [i.impl for i in registry.after_scenario(['A', 'c'])])

    def test_Registry_before_step(self):
        infos = ['before step func', 'before step func1']
        for info in infos:
            registry.add_before_step(info)

        self.assertEqual(infos, [i.impl for i in registry.before_step()])

    def test_Registry_after_step(self):
        infos = ['after step func', 'after step func1']
        for info in infos:
            registry.add_after_step(info)

        self.assertEqual(infos, [i.impl for i in registry.after_step()])

    def test_Registry_before_step_with_tags(self):
        info1 = {'tags': None, 'func': 'before step func'}
        info2 = {'tags': '<A> and <b> and not <c>',
                 'func': 'before step func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'before step func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_before_step(info['func'], info['tags'])

        self.assertEqual([info1['func']], [i.impl for i in registry.before_step([])])
        self.assertEqual([x['func'] for x in infos], [i.impl for i in registry.before_step(['A', 'b'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.before_step(['A', 'b', 'c'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.before_step(['A'])])
        self.assertEqual([info1['func']], [i.impl for i in registry.before_step(['A', 'c'])])

    def test_Registry_after_step_with_tags(self):
        info1 = {'tags': None, 'func': 'after step func'}
        info2 = {'tags': '<A> and <b> and not <c>',
                 'func': 'after step func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)',
                 'func': 'after step func2'}
        infos = [info1, info2, info3]

        for info in infos:
            registry.add_after_step(info['func'], info['tags'])

        self.assertEqual([info1['func']], [i.impl for i in registry.after_step([])])
        self.assertEqual([x['func'] for x in infos], [i.impl for i in registry.after_step(['A', 'b'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.after_step(['A', 'b', 'c'])])
        self.assertEqual([info1['func'], info3['func']], [i.impl for i in registry.after_step(['A'])])
        self.assertEqual([info1['func']], [i.impl for i in registry.after_step(['A', 'c'])])

    def test_Registry__step_positions_of_a_given_file(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func', 'file_name': 'foo.py', 'span': {'start': 1}},
                 {'text': 'Step 1', 'func': 'func1', 'file_name': 'bar.py', 'span': {'start': 3}}]

        for info in infos:
            registry.add_step(info['text'], info['func'], info['file_name'], info['span'])

        positions = registry.get_step_positions('foo.py')

        self.assertIn({'stepValue': 'Say {} to {}', 'span': {'start': 1}}, positions)
        self.assertNotIn({'stepValue': 'Step 1', 'span': {'start': 3}}, positions)

        positions = registry.get_step_positions('bar.py')

        self.assertIn({'stepValue': 'Step 1', 'span': {'start': 3}}, positions)

    def test_Registry_remove_steps_of_a_given_file(self):
        infos = [{'text': 'Say <hello> to <getgauge>', 'func': 'func', 'file_name': 'foo.py'},
                 {'text': 'Step 1', 'func': 'func1', 'file_name': 'bar.py'}]

        for info in infos:
            registry.add_step(info['text'], info['func'], info['file_name'])

        registry.remove_steps('foo.py')

        self.assertFalse(registry.is_implemented('Say {} to {}'))
        self.assertTrue(registry.is_implemented('Step 1'))

    def test_Registry_remove_steps_of_a_given_file_with_duplicate_implementations(self):
        infos = [{'text': 'Step 1', 'func': 'func', 'file_name': 'foo.py'},
                 {'text': 'Step 1', 'func': 'func1', 'file_name': 'bar.py'}]

        for info in infos:
            registry.add_step(info['text'], info['func'], info['file_name'])

        self.assertTrue(registry.has_multiple_impls('Step 1'))

        registry.remove_steps('foo.py')

        self.assertTrue(registry.is_implemented('Step 1'))
        self.assertFalse(registry.has_multiple_impls('Step 1'))

    def test_Registry_is_file_cached(self):
        info = {'text': 'Say <hello> to <getgauge>', 'func': 'func', 'file_name': 'foo.py'}
        registry.add_step(info['text'], info['func'], info['file_name'])

        self.assertTrue(registry.is_file_cached(info['file_name']))

    def test_Registry_add_step_with_empty_arg(self):
        info = {'text': 'Step <>', 'func': 'func', 'file_name': 'foo.py'}

        registry.add_step(info['text'], info['func'], info['file_name'])

        self.assertTrue(registry.is_implemented('Step {}'))

    def test_Registry_get_all_methods_in_should_give_all_the_methods_define_in_that_file(self):
        hooks_infos = [{'func': 'func1', 'file_name': 'foo.py'},
                       {'func': 'func2', 'file_name': 'foo.py'},
                       {'func': 'func3', 'file_name': 'bar.py'}
                       ]
        for info in hooks_infos:
            registry.add_before_step(info['func'], "", info['file_name'])
        step_infos = [{'text': 'Step 1', 'func': 'func', 'file_name': 'foo.py'},
                      {'text': 'Step 1', 'func': 'func1', 'file_name': 'bar.py'}]
        for info in step_infos:
            registry.add_step(info['text'], info['func'], info['file_name'])

        self.assertEqual(3, len(registry.get_all_methods_in("foo.py")))
        self.assertEqual(2, len(registry.get_all_methods_in("bar.py")))

    def tearDown(self):
        global registry
        registry = Registry()


if __name__ == '__main__':
    unittest.main()
