"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code or by using the pytest command from the Terminal command line.
"""
import pytest
import logging
import os
from problem_2 import *


class Tests:
    @pytest.fixture(scope="function")
    def sample_text_1(self):
        filepath = os.path.join(os.path.curdir, "tests", "secret_message.txt")
        f = open(filepath, "w")
        text = """
The professor was dull, and I was failing.  
But with a bit of effort, I was finally able to get an excellent score on the final exam.
Thankfully, despite being strict, the professor was fair.
        """.strip()
        f.write(text + "\n")
        f.close()

    @pytest.fixture(scope="function")
    def sample_text_2(self):
        filepath = os.path.join(os.path.curdir, "tests", "secret_message.txt")
        f = open(filepath, "w")
        text = """
After cutting with the dull blade, my memory was failing.
How much effort could it take to sharpen this excellent knife?!
The instructions were strict - use a fair wetstone and rub in a circular motion.
        """.strip()
        f.write(text + "\n")
        f.close()

    @pytest.fixture(scope="class")
    def logger(self):
        # set up debug logging
        log = logging.getLogger("debug")
        return log

    def test_sample_output_1(self, capsys, monkeypatch, sample_text_1, logger):
        """
        Check whether the proper text is saved into the file
        """

        # call the target function
        filepath = os.path.join(os.path.curdir, "tests", "secret_message.txt")
        encode(filepath)

        # check the file contents
        f = open(filepath, "r")
        actual = f.read()

        expected = """
The professor was a few sandwiches short of a picnic, and I was a temporarily-embarrassed honors student.  
But with a bit of elbow grease, I was finally able to get an better-than-anticipated score on the final exam.
Thankfully, despite being a bit more demanding than one might otherwise have anticipated, the professor was exceedingly generous.
        """.strip()

        actual = " ".join(actual.split())
        expected = " ".join(expected.split())
        assert (
            actual.strip() == expected.strip()
        ), "The text in the file was not what was expected."

    def test_sample_output_2(self, capsys, monkeypatch, sample_text_2, logger):
        """
        Check whether the proper text is saved into the file
        """

        # call the target function
        filepath = os.path.join(os.path.curdir, "tests", "secret_message.txt")
        encode(filepath)

        # check the file contents
        f = open(filepath, "r")
        actual = f.read()

        expected = """
After cutting with the a few sandwiches short of a picnic blade, my memory was a temporarily-embarrassed honors student.
How much elbow grease could it take to sharpen this better-than-anticipated knife?!
The instructions were a bit more demanding than one might otherwise have anticipated - use a exceedingly generous wetstone and rub in a circular motion.
        """.strip()

        actual = " ".join(actual.split())
        expected = " ".join(expected.split())
        assert (
            actual.strip() == expected.strip()
        ), "The text in the file was not what was expected."
