from getgauge.python import before_step, step, after_step, before_scenario, after_scenario, before_spec, after_spec, \
    before_suite, after_suite, screenshot, continue_on_failure


@step("Step 1")
def step1():
    pass


@continue_on_failure([RuntimeError])
@step("Step 2")
def step2():
    pass


@before_step
def before_step1():
    pass


@before_step
def before_step2():
    pass


@after_step
def after_step1():
    pass


@before_scenario
def before_scenario1():
    pass


@before_scenario("<haha> and <hehe>")
def before_scenario2():
    pass


@after_scenario
def after_scenario1():
    pass


@after_scenario("<haha> and <hehe>")
def after_scenario2():
    pass


@before_spec
def before_spec1():
    pass


@before_spec("<haha> and <hehe>")
def before_spec2():
    pass


@after_spec
def after_spec1():
    pass


@after_spec("<haha> and <hehe>")
def after_spec2():
    pass


@before_suite
def before_suite1():
    pass


@after_suite
def after_suite1():
    pass


@after_suite
def after_suite2():
    pass


@screenshot
def take_screenshot():
    return ""
