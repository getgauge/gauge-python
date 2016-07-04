import random
import re

from getgauge import connection
from getgauge.messages.api_pb2 import APIMessage

_api = None


def get_step_value(step_text):
    global _api
    if _api is None:
        return re.sub('<[^<]+?>', '{}', step_text)
    req = APIMessage()
    req.stepValueRequest.stepText = step_text
    req.stepValueRequest.hasInlineTable = False
    req.messageType = APIMessage.GetStepValueRequest
    req.messageId = random.getrandbits(8)
    connection.send_message(req, req, _api)
    res = connection.read_message(_api, APIMessage())
    return res.stepValueResponse.stepValue.stepValue


def connect_to_api():
    global _api
    _api = connection.to_api()


def close_api():
    global _api
    _api = _api.close()
