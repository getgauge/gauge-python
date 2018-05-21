import os
import tempfile
import unittest

from getgauge.messages.messages_pb2 import Message, ParameterPosition
from getgauge.processor import processors
from getgauge.registry import registry


class RefactorTests(unittest.TestCase):
    file = None
    data = None
    path = ''

    def setUp(self):
        RefactorTests.path = os.path.join(tempfile.gettempdir(), 'step_impl.py')
        RefactorTests.file = open(RefactorTests.path, 'w')
        RefactorTests.file.write("""@step("Vowels in English language are <vowels>.")
def assert_default_vowels(given_vowels):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)""")
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

        processors[Message.RefactorRequest](request, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <bsdfdsf>.")
def assert_default_vowels(given_vowels, bsdfdsf):
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

        processors[Message.RefactorRequest](request, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <vowels!2_ab%$>.")
def assert_default_vowels(given_vowels, arg1):
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

        processors[Message.RefactorRequest](request, response, None)
        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels> <!%$>.")
def assert_default_vowels(given_vowels, arg1):
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

        processors[Message.RefactorRequest](request, response, None)

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

        processors[Message.RefactorRequest](request, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <vowels>.")
def assert_default_vowels(given_vowels):
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

        processors[Message.RefactorRequest](request, response, None)

        actual_data = self.getActualText()

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)

        expected = """@step("Vowels in English language is <bsdfdsf>.")
def assert_default_vowels(bsdfdsf):
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

        processors[Message.RefactorRequest](request, response, None)

        expected = """@step("Vowels in English language is <vowels> <bsdfdsf>.")
def assert_default_vowels(given_vowels, bsdfdsf):
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

        processors[Message.RefactorRequest](request, response, None)

        self.assertEqual(Message.RefactorResponse, response.messageType)
        self.assertEqual(True,
                         response.refactorResponse.success,
                         response.refactorResponse.error)

        self.assertEqual([RefactorTests.path],
                         response.refactorResponse.filesChanged)
        expected = """@step("Vowels in English language is <vowels> <vowels!2_ab%$>.")
def assert_default_vowels(given_vowels, arg1):
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)
"""
        self.assertEqual(expected, response.refactorResponse.fileChanges[0].fileContent)
        self.assertEqual(old_content, self.getActualText())
        diff_contents = [diff.content for diff in response.refactorResponse.fileChanges[0].diffs]
        self.assertIn('("Vowels in English language is <vowels> <vowels!2_ab%$>.")', diff_contents)
        self.assertIn('given_vowels, arg1', diff_contents)

    def getActualText(self):
        _file = open(RefactorTests.path, 'r+')
        actual_data = _file.read()
        _file.seek(0)
        _file.truncate()
        _file.write(RefactorTests.data)
        _file.close()
        return actual_data
