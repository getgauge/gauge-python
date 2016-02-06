import re
import unittest

from getgauge.registry import registry, Registry


class RegistryTests(unittest.TestCase):
    def setUp(self):
        global registry
        registry = Registry()

    def test_Registry_add_step_definition(self):
        infos = [{'text': "Say <hello> to <getgauge>", 'func': 'func'}, {'text': "Step 1", 'func': 'func1'}]
        for info in infos:
            registry.add_step_definition(info['text'], info['func'], "")

        self.assertEqual([info['text'] for info in infos].sort(), registry.all_steps().sort())
        for info in infos:
            parsed_step_text = re.sub('<[^<]+?>', '{}', info['text'])
            self.assertEqual(info['func'], registry.get_info(parsed_step_text).impl)

    def test_Registry_get_step_info(self):
        infos = [{'text': "Say <hello> to <getgauge>", 'func': 'func'}, {'text': "Step 1", 'func': 'func1'}]
        for info in infos:
            registry.add_step_definition(info['text'], info['func'], "")

        self.assertEqual("Say <hello> to <getgauge>", registry.get_info("Say {} to {}").step_text)
        self.assertEqual("Step 1", registry.get_info("Step 1").step_text)
        self.assertEqual(None, registry.get_info("Step21").step_text)

    def test_Registry_is_step_implemented(self):
        infos = [{'text': "Say <hello> to <getgauge>", 'func': 'func'}, {'text': "Step 1", 'func': 'func1'}]
        for info in infos:
            registry.add_step_definition(info['text'], info['func'], "")

        for info in infos:
            parsed_step_text = re.sub('<[^<]+?>', '{}', info['text'])
            self.assertTrue(registry.is_step_implemented(parsed_step_text))

    def test_Registry_before_suite(self):
        infos = ['before suite func', 'before suite func1']
        for info in infos:
            registry.add_before_suite(info)

        self.assertEqual(infos, registry.before_suite())

    def test_Registry_after_suite(self):
        infos = ['after suite func', 'after suite func1']
        for info in infos:
            registry.add_after_suite(info)

        self.assertEqual(infos, registry.after_suite())

    def test_Registry_before_spec(self):
        infos = ['before spec func', 'before spec func1']
        for info in infos:
            registry.add_before_spec(info)

        self.assertEqual(infos, registry.before_spec())

    def test_Registry_after_spec(self):
        infos = ['after spec func', 'after spec func1']
        for info in infos:
            registry.add_after_spec(info)

        self.assertEqual(infos, registry.after_spec())

    def test_Registry_before_spec_with_tags(self):
        info1 = {'tags': None, 'func': 'before spec func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'before spec func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'before spec func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_before_spec(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.before_spec([]))
        self.assertEqual([x['func'] for x in infos], registry.before_spec(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.before_spec(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.before_spec(['A']))
        self.assertEqual([info1['func']], registry.before_spec(['A', 'c']))

    def test_Registry_after_spec_with_tags(self):
        info1 = {'tags': None, 'func': 'after spec func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'after spec func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'after spec func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_after_spec(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.after_spec([]))
        self.assertEqual([x['func'] for x in infos], registry.after_spec(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.after_spec(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.after_spec(['A']))
        self.assertEqual([info1['func']], registry.after_spec(['A', 'c']))

    def test_Registry_before_scenario(self):
        infos = ['before scenario func', 'before scenario func1']
        for info in infos:
            registry.add_before_scenario(info)

        self.assertEqual(infos, registry.before_scenario())

    def test_Registry_after_scenario(self):
        infos = ['after scenario func', 'after scenario func1']
        for info in infos:
            registry.add_after_scenario(info)

        self.assertEqual(infos, registry.after_scenario())

    def test_Registry_before_scenario_with_tags(self):
        info1 = {'tags': None, 'func': 'before scenario func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'before scenario func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'before scenario func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_before_scenario(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.before_scenario([]))
        self.assertEqual([x['func'] for x in infos], registry.before_scenario(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.before_scenario(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.before_scenario(['A']))
        self.assertEqual([info1['func']], registry.before_scenario(['A', 'c']))

    def test_Registry_after_scenario_with_tags(self):
        info1 = {'tags': None, 'func': 'after scenario func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'after scenario func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'after scenario func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_after_scenario(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.after_scenario([]))
        self.assertEqual([x['func'] for x in infos], registry.after_scenario(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.after_scenario(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.after_scenario(['A']))
        self.assertEqual([info1['func']], registry.after_scenario(['A', 'c']))

    def test_Registry_before_step(self):
        infos = ['before step func', 'before step func1']
        for info in infos:
            registry.add_before_step(info)

        self.assertEqual(infos, registry.before_step())

    def test_Registry_after_step(self):
        infos = ['after step func', 'after step func1']
        for info in infos:
            registry.add_after_step(info)

        self.assertEqual(infos, registry.after_step())

    def test_Registry_before_step_with_tags(self):
        info1 = {'tags': None, 'func': 'before step func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'before step func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'before step func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_before_step(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.before_step([]))
        self.assertEqual([x['func'] for x in infos], registry.before_step(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.before_step(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.before_step(['A']))
        self.assertEqual([info1['func']], registry.before_step(['A', 'c']))

    def test_Registry_after_step_with_tags(self):
        info1 = {'tags': None, 'func': 'after step func'}
        info2 = {'tags': '<A> and <b> and not <c>', 'func': 'after step func1'}
        info3 = {'tags': '<A> and (<b> or not <c>)', 'func': 'after step func2'}
        infos = [info1, info2, info3]
        for info in infos:
            registry.add_after_step(info['func'], info['tags'])

        self.assertEqual([info1['func']], registry.after_step([]))
        self.assertEqual([x['func'] for x in infos], registry.after_step(['A', 'b']))
        self.assertEqual([info1['func'], info3['func']], registry.after_step(['A', 'b', 'c']))
        self.assertEqual([info1['func'], info3['func']], registry.after_step(['A']))
        self.assertEqual([info1['func']], registry.after_step(['A', 'c']))

    def tearDown(self):
        global registry
        registry = Registry()


if __name__ == '__main__':
    unittest.main()
