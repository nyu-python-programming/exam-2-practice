"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code or by using the pytest command from the Terminal command line.
"""
import pytest
import logging
from problem_3 import *


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

    def test_valid_homeowner_1(self, capsys, monkeypatch, logger):
        """
        Check whether a homeowner with valid income will qualify.
        """

        mock_data = {"input": ["$30,000", "y", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "You qualify!"
        not_expected = "Sorry, you don't qualify."
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 2
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_valid_homeowner_2(self, capsys, monkeypatch, logger):
        """
        Check whether a homeowner with valid income will qualify.
        """

        mock_data = {"input": ["$1,000,000", "y", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "You qualify!"
        not_expected = "Sorry, you don't qualify."
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 2
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_invalid_homeowner_1(self, capsys, monkeypatch, logger):
        """
        Check whether a homeowner with invalid income will qualify.
        """

        mock_data = {"input": ["$20,000", "y", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "Sorry, you don't qualify."
        not_expected = "You qualify!"
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 2
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_invalid_homeowner_2(self, capsys, monkeypatch, logger):
        """
        Check whether a homeowner with invalid income will qualify.
        """

        mock_data = {"input": ["$29,999", "y", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "Sorry, you don't qualify."
        not_expected = "You qualify!"
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 2
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_valid_renter_1(self, capsys, monkeypatch, logger):
        """
        Check whether a renter with valid income will qualify.
        """

        mock_data = {"input": ["$100,000", "n", "$5,000", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "You qualify!"
        not_expected = "Sorry, you don't qualify."
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 3
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_valid_renter_2(self, capsys, monkeypatch, logger):
        """
        Check whether a renter with valid income will qualify.
        """

        mock_data = {"input": ["$50,000", "n", "$2,400", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "You qualify!"
        not_expected = "Sorry, you don't qualify."
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 3
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_invalid_renter_1(self, capsys, monkeypatch, logger):
        """
        Check whether a renter with invalid income will qualify.
        """

        mock_data = {"input": ["$100,000", "n", "$5,001", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "Sorry, you don't qualify."
        not_expected = "You qualify!"
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 3
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."

    def test_invalid_renter_2(self, capsys, monkeypatch, logger):
        """
        Check whether a renter with invalid income will qualify.
        """

        mock_data = {"input": ["$50,000", "n", "$2,501", "foo", "bar"]}
        call_counter = {
            "input": 0,
        }
        test_inputs = mock_data["input"].copy()  # a copy to refer to later
        # mock the input function
        self.mock_input(mock_data, call_counter, monkeypatch)

        # call the target function
        qualify()

        # capture the printed output
        captured = capsys.readouterr()  # capture print output
        actual = captured.out.lower().strip()  # split by line break

        # make sure the qualification is correct
        expected = "Sorry, you don't qualify."
        not_expected = "You qualify!"
        assert (
            expected.lower() in actual.lower()
        ), f'The qualify function did not print "{expected}" as expected when testing the user inputs: {test_inputs}.'
        assert (
            not_expected.lower() not in actual.lower()
        ), f'The qualify function unexpectedly printed "{not_expected}" when testing the user inputs: {test_inputs}.'

        # make sure the function was called the correct number of times
        expected = 3
        actual = call_counter["input"]
        assert (
            actual == expected
        ), f"Expected the input function to be called {expected} times when the user inputs the test data: {test_inputs}; instead, it was called {actual} times."
