import os
import sys
import tempfile
import unittest

from getgauge import processor
from getgauge.messages.messages_pb2 import Message, ParameterPosition
from getgauge.registry import registry


class RefactorTests(unittest.TestCase):
    file = None
    data = None
    path = ''

    def setUp(self):
        self.preservesNewlines = True
        RefactorTests.path = os.path.join(tempfile.gettempdir(), 'step_impl.py')
        RefactorTests.file = open(RefactorTests.path, 'w')
        RefactorTests.file.write("""@step("Vowels in English language are <vowels>.")
def assert_default_vowels(arg0):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)\n""")
        RefactorTests.file.close()
        RefactorTests.file = open(RefactorTests.path, 'r')
        RefactorTests.data = RefactorTests.file.read()
        RefactorTests.file.close()
        registry.add_step('Vowels in English language are <vowels>.', None,
                          RefactorTests.path)

    def tearDown(self):
        registry.clear()

    def test_Processor_refactor_request_with_add_param(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is \
<vowels> <bsdfdsf>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels', 'bsdfdsf'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([position, param_position])

        processor.refactor_step(request.refactorRequest, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <bsdfdsf>.")
def assert_default_vowels(arg0, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request_with_add_param_and_invalid_identifier(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is \
<vowels> <vowels!2_ab%$>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels', 'vowels!2_ab%$'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([position, param_position])

        processor.refactor_step(request.refactorRequest, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <vowels!2_ab%$>.")
def assert_default_vowels(arg0, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request_with_add_param_and_only_invalid_identifier(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is \
<vowels> <!%$>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels', '!%$'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([position, param_position])

        processor.refactor_step(request.refactorRequest, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <!%$>.")
def assert_default_vowels(arg0, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request_with_remove_param(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is.'

        processor.refactor_step(request.refactorRequest, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is.")
def assert_default_vowels():
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is <vowels>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        request.refactorRequest.paramPositions.extend([position])

        processor.refactor_step(request.refactorRequest, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels>.")
def assert_default_vowels(arg0):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request_with_add_and_remove_param(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is <bsdfdsf>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {}.'
        request.refactorRequest.newStepValue.parameters.extend(['bsdfdsf'])
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 0
        request.refactorRequest.paramPositions.extend([param_position])

        processor.refactor_step(request.refactorRequest, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <bsdfdsf>.")
def assert_default_vowels(arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_processor_refactor_request_with_insert_param(self):
        response = Message()
        request = Message()
        request.refactorRequest.saveChanges = True

        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.oldStepValue.parameterizedStepValue = 'Vowels in English language are <vowels>.'

        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is <a> <vowels>.'
        request.refactorRequest.newStepValue.parameters.extend(['a', 'vowels'])
        param1_position = ParameterPosition()
        param1_position.oldPosition = -1
        param1_position.newPosition = 0

        param2_position = ParameterPosition()
        param2_position.oldPosition = 0
        param2_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([param1_position, param2_position])

        processor.refactor_step(request.refactorRequest, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <a> <vowels>.")
def assert_default_vowels(arg1, arg0):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, actual_data)

    def test_Processor_refactor_request_without_save_change_with_add_param(self):
        response = Message()
        request = Message()

        request.refactorRequest.saveChanges = False
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language \
is <vowels> <bsdfdsf>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels', 'bsdfdsf'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([position, param_position])

        old_content = self.getActualText()

        processor.refactor_step(request.refactorRequest, response, None)

        expected = """@step("Vowels in English language is <vowels> <bsdfdsf>.")
def assert_default_vowels(arg0, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        self.assertEqual(RefactorTests.path, response.refactorResponse.fileChanges[0].fileName)
        self.assertEqual(expected, response.refactorResponse.fileChanges[0].fileContent)
        self.assertEqual(old_content, self.getActualText())

    def test_Processor_refactor_request_without_save_changes_add_param_and_invalid_identifier(self):
        response = Message()
        request = Message()

        request.refactorRequest.saveChanges = False
        request.refactorRequest.oldStepValue.stepValue = 'Vowels in English language are {}.'
        request.refactorRequest.oldStepValue.parameters.append('vowels')
        request.refactorRequest.newStepValue.parameterizedStepValue = 'Vowels in English language is \
<vowels> <vowels!2_ab%$>.'
        request.refactorRequest.newStepValue.stepValue = 'Vowels in English language is {} {}.'
        request.refactorRequest.newStepValue.parameters.extend(['vowels', 'vowels!2_ab%$'])
        position = ParameterPosition()
        position.oldPosition = 0
        position.newPosition = 0
        param_position = ParameterPosition()
        param_position.oldPosition = -1
        param_position.newPosition = 1
        request.refactorRequest.paramPositions.extend([position, param_position])

        old_content = self.getActualText()

        processor.refactor_step(request.refactorRequest, response, None)

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)
        expected = """@step("Vowels in English language is <vowels> <vowels!2_ab%$>.")
def assert_default_vowels(arg0, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, response.refactorResponse.fileChanges[0].fileContent)
        self.assertEqual(old_content, self.getActualText())
        diff_contents = [diff.content for diff in response.refactorResponse.fileChanges[0].diffs]
        self.assertIn('"Vowels in English language is <vowels> <vowels!2_ab%$>."', diff_contents)
        self.assertIn('arg0, arg1', diff_contents)

    def getActualText(self):
        _file = open(RefactorTests.path, 'r+')
        actual_data = _file.read()
        _file.seek(0)
        _file.truncate()
        _file.write(RefactorTests.data)
        _file.close()
        return actual_data

