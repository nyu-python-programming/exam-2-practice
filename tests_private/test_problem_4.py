"""PRIVATE hidden tests for problem_4.generate_shopping_list (not shipped)."""
from problem_4 import generate_shopping_list


def test_uppercase_input_is_lowercased(mock_input, capsys):
    mock_input(["TOMATOES", "2LB", "finished"])
    generate_shopping_list()
    out = capsys.readouterr().out
    assert "- tomatoes (2lb)" in out, "items and quantities should be lowercased"


def test_done_also_ends_the_loop(mock_input, capsys):
    # The spec accepts either "finished" or "done" to stop.
    mock_input(["Apples", "3", "done"])
    generate_shopping_list()
    out = capsys.readouterr().out
    assert "- apples (3)" in out
    assert "Thank you!" in out


def test_order_preserved(mock_input, capsys):
    mock_input(["Arugula", "2", "Tomatoes", "2lb", "finished"])
    generate_shopping_list()
    out = capsys.readouterr().out
    assert out.index("- arugula (2)") < out.index("- tomatoes (2lb)"), \
        "items should appear in the order entered"
