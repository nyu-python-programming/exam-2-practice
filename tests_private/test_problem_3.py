"""PRIVATE hidden tests for problem_3.qualify (not shipped to students).

Focuses on the boundary conditions the visible suite under-covers:
  * income >= 30000 qualifies (exactly 30000 is OK)
  * a renter's monthly rent must NOT EXCEED 5% of yearly income (1500 on 30000)
  * a homeowner's rent is irrelevant
"""
from problem_3 import qualify


def _out(capsys):
    return capsys.readouterr().out


def test_owner_exactly_min_income_qualifies(mock_input, capsys):
    mock_input(["30000", "y"])
    qualify()
    assert "You qualify!" in _out(capsys)


def test_owner_below_min_income_fails(mock_input, capsys):
    mock_input(["29999", "y"])
    qualify()
    assert "income is too low" in _out(capsys)


def test_renter_rent_exactly_five_percent_qualifies(mock_input, capsys):
    # 5% of 30000/12 ... spec: monthly rent must not exceed 5% of yearly income.
    mock_input(["30000", "n", "1500"])
    qualify()
    assert "You qualify!" in _out(capsys)


def test_renter_rent_just_over_threshold_fails(mock_input, capsys):
    mock_input(["30000", "n", "1501"])
    qualify()
    assert "rent is too high" in _out(capsys)


def test_owner_ignores_high_rent_value(mock_input, capsys):
    # An owner is never asked about rent, so two inputs suffice and they qualify.
    mock_input(["50000", "y"])
    qualify()
    assert "You qualify!" in _out(capsys)
