.. _features:

Features
--------

If you are new to Gauge, please consult the `Gauge documentation`_ to know about how Gauge works.

Step implementation
~~~~~~~~~~~~~~~~~~~



Use the ``@step(<step-text>)`` to implement your steps. For example:

    ::

        from getgauge.python import step

        @step("The word <word> has <number> vowels.")
        def hello(a, b):
            print("The word {} has {} vowels.".format(a, b))


Multiple step names
^^^^^^^^^^^^^^^^^^^

To implement the same function for multiple step names (aka, step aliases), pass an ``array`` of ``strings`` as the first argument to ``@step()``. For example:

   ::

       from getgauge.python import step

       @step(["Create a user <user name>", "Create another user <user name>"])
       def hello(user_name):
           print("create {}.".format(user_name))

Parameters
^^^^^^^^^^
Steps can be defined to take values as parameters so that they can be re-used with different parameter values.

String
""""""
   ::

       from getgauge.python import step

       @step("Create another user <user name>")
       def hello(user_name):
           print("create {}.".format(user_name))


Table
"""""
   ::

       * Create a product
           |Title         |Description         |Author        |Price|
           |--------------|--------------------|--------------|-----|
           |Go Programming|ISBN: 978-1453636671|John P. Baugh |25.00|
           |The Way to Go |ISBN: 978-1469769165|Ivo Balbaert  |20.00|
           |Go In Action  |ISBN: 9781617291784 |Brian Ketelsen|30.00|
           |Learning Go   |ebook               |Miek Gieben   |0.00 |


       @step('Create a product <table>')
       def create_product(table):
       for row in table:
           PageFactory.create_page.create(row[0], row[1], row[2], row[3])


Execution Hooks
~~~~~~~~~~~~~~~

Test execution hooks can be used to run arbitrary test code as different levels during the test suite execution. For more details on hooks, refer `Gauge documentation`_

.. _Gauge documentation: http://getgauge.io/documentation/user/current/execution/execution_hooks.html

-  ``before_step``

-  ``after_step``

-  ``before_scenario``

-  ``after_scenario``

-  ``before_spec``

-  ``after_spec``

-  ``before_suite``

-  ``after_suite``

   ::

       from getgauge.python import before_step, after_scenario

       @before_step
       def before_step_hook():
           print("after scenario hook")

Execution Context
^^^^^^^^^^^^^^^^^

To get additional information about the current specification, scenario and step executing, an additional ``context`` parameter can be added to the hooks method.

   ::

       from getgauge.python import before_step, after_scenario

       @before_step
       def before_step_hook(context):
           print(context)

Tagged Execution Hooks
^^^^^^^^^^^^^^^^^^^^^^

Execution hooks can be run for specify tags. This will ensure that the hook runs only on scenarios and specifications that have the required tags. The following ``after_scenario`` hook will be run if the scenario has ``hello`` and ``hi``.

   ::

       @after_scenario("<hello> and <hi>")
       def after_scenario_hook():
           print("after scenario hook with tag")

Complex tags expression can alse be used like: ``<hello> and <hi> or not <hey>``.

.. note::
   Tagged execution hooks are not supported for ``before_suite`` and ``after_suite`` hooks.

Custom messages to report
~~~~~~~~~~~~~~~~~~~~~~~~~

**Messages.write_message(<string>)**: Use the ``Messages.write_message(<String>)`` function to send custom messages to ``gauge`` in your step implementations. This method takes only one string as an argument. You can call it multiple times to send multiple messages within the same step.

Example:


    ::

       from getgauge.python import Messages

       Messages.write_message("After scenario")


Data Stores
~~~~~~~~~~~

Step implementations can share custom data across scenarios, specifications and suites using data stores.
There are 3 different types of data stores based on the lifecycle of when it gets cleared.

Scenario store
^^^^^^^^^^^^^^

This data store keeps values added to it in the lifecycle of the scenario execution. Values are cleared after every scenario executes.

**Store a value:**

.. code::

    from getgauge.python import DataStoreFactory
    DataStoreFactory.scenario_data_store().put(key, value)

**Retrieve a value:**

.. code::

    DataStoreFactory.scenario_data_store().get(key)

Specification store
^^^^^^^^^^^^^^^^^^^

This data store keeps values added to it in the lifecycle of the
specification execution. Values are cleared after every specification
executes.

**Store a value:**

.. code::

    from getgauge.python import DataStoreFactory
    DataStoreFactory.spec_data_store().put(key, value)

**Retrieve a value:**

.. code::

    DataStoreFactory.spec_data_store().get(key)

Suite store
^^^^^^^^^^^

This data store keeps values added to it in the lifecycle of the entire
suite’s execution. Values are cleared after entire suite executes.

**Store a value:**

.. code::

    from getgauge.python import DataStoreFactory
    DataStoreFactory.suite_data_store().put(key, value);

**Retrieve a value:**

.. code::

    DataStoreFactory.suite_data_store().get(key);

.. note::
    Suite Store is not advised to be used when executing specs in parallel. The values are not retained between parallel streams of execution.


Refactoring
~~~~~~~~~~~

``gauge-python`` supports refactoring your specifications and step implementations. Refactoring can be done using the following command signature:

   .. code:: sh

       $ gauge --refactor "Existing step text" "New step text"

The python runner plugin will alter the step text in the step decorator and function signature.

Debugging
~~~~~~~~~

Gauge-Python supports debugging your test implementation code using `pbd`_.

.. _pbd: https://docs.python.org/2/library/pdb.html

   ::

       import pdb

The typical usage to break into the debugger from a running program is to insert

   ::

       pdb.set_trace()

Execution will stop where it finds the above statement and you can debug.

Custom screenshot hook
~~~~~~~~~~~~~~~~~~~~~~

You can specify a custom function to grab a screenshot on step failure. By default, gauge-python takes screenshot of the current screen using the gauge_screenshot binary.
Use screenshot decorator on the custom screenshot function and it should return a base64 encoded string of the image data that gauge-python will use as image content on failure.

   ::

       from getgauge.python import screenshot
       @screenshot
       def take_screenshot():
           return "base64encodedstring"

