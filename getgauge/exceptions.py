class MultipleImplementationFoundException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class SkipScenarioException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
