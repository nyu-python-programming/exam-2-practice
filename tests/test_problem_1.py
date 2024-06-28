"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code or by using the pytest command from the Terminal command line.
"""
import pytest
import logging
from problem_1 import *


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

    def test_valid_proper_noun(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying proper nouns.
        """

        mock_data = {
            "input": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        }
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # loop through each test input
        i = 1
        num_inputs = len(mock_data["input"])
        for day in range(num_inputs):
            # call the target function
            actual = get_valid_day()

            # assert the correct value was returned
            expected = i
            assert (
                actual == expected
            ), f"Incorrect return value from get_valid_day when trying to run the function with a variety of test inputs: {test_inputs}."  # number of the day
            i += 1

        # make sure the function was called the correct number of times
        logger.warning(num_inputs)
        actual = call_counter["input"]
        expected = num_inputs
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times with {num_inputs} tests of the get_valid_day function; instead, input was called {actual} times."

    def test_valid_abbreviated_proper_noun(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying abbreviated proper nouns.
        """

        mock_data = {"input": ["Mon", "Tues", "Weds", "Thurs", "Fri", "Sat", "Sun"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # loop through each test input
        i = 1
        num_inputs = len(mock_data["input"])
        for day in range(num_inputs):
            # call the target function
            actual = get_valid_day()

            # assert the correct value was returned
            expected = i
            assert (
                actual == expected
            ), f"Incorrect return value from get_valid_day when trying to run the function with a variety of test inputs: {test_inputs}."  # number of the day
            i += 1

        # make sure the function was called the correct number of times
        logger.warning(num_inputs)
        actual = call_counter["input"]
        expected = num_inputs
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times with {num_inputs} tests of the get_valid_day function; instead, input was called {actual} times."

    def test_valid_ints(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying ints.
        """

        mock_data = {"input": ["1", "2", "3", "4", "5", "6", "7"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # loop through each test input
        i = 1
        num_inputs = len(mock_data["input"])
        for day in range(num_inputs):
            # call the target function
            actual = get_valid_day()

            # assert the correct value was returned
            expected = i
            assert (
                actual == expected
            ), f"Incorrect return value from get_valid_day when trying to run the function with a variety of test inputs: {test_inputs}."  # number of the day
            i += 1

        # make sure the function was called the correct number of times
        logger.warning(num_inputs)
        actual = call_counter["input"]
        expected = num_inputs
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times with {num_inputs} tests of the get_valid_day function; instead, input was called {actual} times."

    def test_invalid_proper_noun(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying invalid proper nouns.
        """

        mock_data = {
            "input": ["foo", "bar", "Wednesday", "Tuesday"],
        }
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later

        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        actual = get_valid_day()

        # assert the correct value was returned
        expected = 3
        assert (
            actual == expected
        ), f"Incorrect return value from get_valid_day when trying these test inputs: {test_inputs}."  # number of the day

        # make sure the function was called the correct number of times
        actual = call_counter["input"]
        expected = 3
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times from the get_valid_day function when testing the following sequence of user inputs: {test_inputs}; instead, input was called {actual} times."

    def test_valid_abbreviated_proper_noun(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying invalid abbreviated proper nouns.
        """

        mock_data = {"input": ["foo", "bar", "baz", "Thurs", "Mon"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        actual = get_valid_day()

        # assert the correct value was returned
        expected = 4
        assert (
            actual == expected
        ), f"Incorrect return value from get_valid_day when trying these test inputs: {test_inputs}."  # number of the day

        # make sure the function was called the correct number of times
        actual = call_counter["input"]
        expected = 4
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times from the get_valid_day function when testing the following sequence of user inputs: {test_inputs}; instead, input was called {actual} times."

    def test_invalid_ints(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying ints.
        """

        mock_data = {"input": ["-1", "0", "10", "1", "2"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        actual = get_valid_day()

        # assert the correct value was returned
        expected = 1
        assert (
            actual == expected
        ), f"Incorrect return value from get_valid_day when trying these test inputs: {test_inputs}."  # number of the day

        # make sure the function was called the correct number of times
        actual = call_counter["input"]
        expected = 4
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times from the get_valid_day function when testing the following sequence of user inputs: {test_inputs}; instead, input was called {actual} times."

    def test_case_insensitivity(self, capsys, monkeypatch, logger):
        """
        Check whether the return value is correct when supplying ints.
        """

        mock_data = {"input": ["MONDAY", "tuesday", "weDNESday", "thurs", "frI"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # loop through each test input
        i = 1
        num_inputs = len(mock_data["input"])
        for day in range(num_inputs):
            # call the target function
            actual = get_valid_day()

            # assert the correct value was returned
            expected = i
            assert (
                actual == expected
            ), f"Incorrect return value from get_valid_day when trying to run the function with a variety of test inputs: {test_inputs}."  # number of the day
            i += 1

        # make sure the function was called the correct number of times
        logger.warning(num_inputs)
        actual = call_counter["input"]
        expected = num_inputs
        assert (
            actual == expected
        ), f"Expected to call the input function {expected} times with {num_inputs} tests of the get_valid_day function; instead, input was called {actual} times."
