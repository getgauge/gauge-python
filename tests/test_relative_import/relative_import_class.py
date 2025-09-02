from getgauge.python import step, Messages


class BaseSample:
    def __init__(self) -> None:
        pass

class Sample(BaseSample):
    def __init__(self) -> None:
        pass

    # Gauge step implementation in a class
    @step('Greet <name> from inside the class')
    def greetings_from_class(self, name):
        Messages.write_message("Hello from inside the class, {0}".format(name))


# Gauge step implementation outside class
@step('Greet <name> from outside the class')
def greetings_from_outside_the_class(name):
    Messages.write_message("Hello from outside the class, {0}".format(name))