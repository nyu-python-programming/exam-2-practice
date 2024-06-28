"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code.
"""
import pytest
import logging
from problem_4 import *


class Tests:
    @pytest.fixture(scope="class")
    def logger(self):
        # set up debug logging
        log = logging.getLogger("debug")
        return log

    def mock_input(self, mock_data, call_counter, monkeypatch):
        """
        Mock the builtin input function
        :param mock_data: Dictionary of data to mock.
        :param call_counter: Dictionary of counters for function calls
        :param monkeypatch: pytest's monkeypatch object
        """

        # mock the input function
        def new_input(message):
            call_counter["input"] += 1
            return mock_data["input"].pop(0)

        monkeypatch.setattr("builtins.input", lambda x: new_input(x))

    def test_lowercase(self, capsys, monkeypatch, logger):
        """
        Check whether all input is converted to lowercase
        """

        mock_data = {
            "input": [
                "ARUGULA",
                "3LB",
                "Tomatoes",
                "60LB",
                "chEDDAR",
                "17 Blocks",
                "finished",
            ]
        }
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        num_inputs = len(mock_data["input"])

        # call the target function
        generate_shopping_list()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the output is correct
        assert (
            "arugula" in actual
        ), f'The text, "arugula", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "3lb" in actual
        ), f'The text, "3lb", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "tomatoes" in actual
        ), f'The text, "tomatoes", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "60lb" in actual
        ), f'The text, "60lb", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "cheddar" in actual
        ), f'The text, "cheddar", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "17 blocks" in actual
        ), f'The text, "17 blocks", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = num_inputs
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times by the generate_shopping_cart function when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_item_output(self, capsys, monkeypatch, logger):
        """
        Check whether each individual item is output correctly.
        """

        mock_data = {
            "input": [
                "bok choy",
                "6lb",
                "smoked chub",
                "40lb",
                "tomatoes",
                "60lb",
                "cheddar",
                "17 blocks",
                "finished",
            ]
        }
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        num_inputs = len(mock_data["input"])

        # call the target function
        generate_shopping_list()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the output is correct
        assert (
            "- bok choy (6lb)" in actual
        ), f'The text, "- bok choy (6lb)", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "- smoked chub (40lb)" in actual
        ), f'The text, "- smoked chub (40lb)", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "- tomatoes (60lb)" in actual
        ), f'The text, "- tomatoes (60lb)", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'
        assert (
            "- cheddar (17 blocks)" in actual
        ), f'The text, "- cheddar (17 blocks)", was unexpectedly not printed by the generate_shopping_list function when testing with the inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = num_inputs
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times by the generate_shopping_cart function when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_overall_output(self, capsys, monkeypatch, logger):
        """
        Check whether overall output is exactly correct
        """

        mock_data = {
            "input": [
                "tomatoes",
                "60lb",
                "bok choy",
                "6lb",
                "cheddar",
                "17 blocks",
                "smoked chub",
                "40lb",
                "finished",
            ]
        }
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        num_inputs = len(mock_data["input"])

        # call the target function
        generate_shopping_list()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the output is exactly completelycorrect
        expected = """
        Welcome to the shopping list generator!

        Here is your complete shopping list:
        - tomatoes (60lb)
        - bok choy (6lb)
        - cheddar (17 blocks)
        - smoked chub (40lb)

        Thank you!
        """.strip()

        # remove multiple whitespaces and convert to lowercase
        actual = " ".join(actual.split()).lower()
        expected = " ".join(expected.split()).lower()
        # logger.warning(actual)
        # logger.warning(expected)

        # assert the output is correct
        assert actual == expected

        # make sure the function was called the correct number of times
        expected = num_inputs
        actual = call_counter["input"]
        test_inputs = mock_data["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times by the generate_shopping_cart function when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."
