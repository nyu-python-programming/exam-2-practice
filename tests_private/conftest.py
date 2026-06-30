"""
Shared helpers for the PRIVATE (instructor-only) hidden test suite.

This suite is NOT distributed to students. It is run on the grader's machine
(e.g. by tools/score_all.py) against each submission to catch solutions that
were tuned only to the visible tests. It exercises spec-required edge cases the
visible suite under-covers -- deliberately only asserting behavior the exam
spec clearly requires, to keep false failures low.
"""
import pytest


@pytest.fixture
def mock_input(monkeypatch):
    """Return a factory that feeds a list of inputs to builtins.input."""
    state = {"calls": 0}

    def feed(values):
        queue = list(values)

        def fake(_prompt=""):
            state["calls"] += 1
            return queue.pop(0)

        monkeypatch.setattr("builtins.input", fake)
        return state

    return feed
