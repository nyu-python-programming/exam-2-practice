"""PRIVATE hidden tests for problem_2.encode (not shipped to students)."""
import os
from problem_2 import encode


def _write(tmp_path, text):
    p = tmp_path / "secret_message.txt"
    p.write_text(text)
    return str(p)


def test_returns_false_and_unchanged_when_no_targets(tmp_path):
    original = "Nothing here matches any target phrase at all.\n"
    path = _write(tmp_path, original)
    result = encode(path)
    assert result is False or result == False, "encode should return False when nothing swapped"
    assert open(path).read() == original, "file must be unchanged when no words swapped"


def test_returns_true_when_something_swapped(tmp_path):
    path = _write(tmp_path, "The lecture was dull.\n")
    assert encode(path), "encode should return a truthy value when a word is swapped"
    assert "a few sandwiches short of a picnic" in open(path).read()


def test_multiple_occurrences_all_replaced(tmp_path):
    path = _write(tmp_path, "dull and dull and still dull\n")
    encode(path)
    out = open(path).read()
    assert "dull" not in out, "every occurrence of a target word should be replaced"
    assert out.count("a few sandwiches short of a picnic") == 3


def test_all_six_replacements(tmp_path):
    text = "dull failing effort excellent strict fair"
    path = _write(tmp_path, text)
    encode(path)
    out = open(path).read()
    for phrase in [
        "a few sandwiches short of a picnic",
        "a temporarily-embarrassed honors student",
        "elbow grease",
        "better-than-anticipated",
        "a bit more demanding than one might otherwise have anticipated",
        "exceedingly generous",
    ]:
        assert phrase in out, f"missing replacement: {phrase}"
