from getgauge.python import step, before_scenario, Messages, data_store


def number_of_vowels(word):
    vowels = data_store.scenario["vowels"]
    return len([elem for elem in list(word) if elem in vowels])


# --------------------------
# Gauge step implementations
# --------------------------

@step("The word <word> has <number> vowels.")
def assert_no_of_vowels_in(word, number):
    assert str(number) == str(number_of_vowels(word))


@step("Vowels in English language are <vowels>.")
def assert_default_vowels(given_vowels):
    vowels = data_store.scenario["vowels"]
    Messages.write_message("Given vowels are {0}".format(given_vowels))
    assert given_vowels == "".join(vowels)


@step("Almost all words have vowels <table>")
def assert_words_vowel_count(table):
    actual = [str(number_of_vowels(word)) for word in table.get_column_values_with_name("Word")]
    expected = [str(count) for count in table.get_column_values_with_name("Vowel Count")]
    assert expected == actual


# ---------------
# Execution Hooks
# ---------------

@before_scenario()
def before_scenario_hook():
    data_store.scenario["vowels"] = ["a", "e", "i", "o", "u"]
