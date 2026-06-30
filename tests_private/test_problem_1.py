"""PRIVATE hidden tests for problem_1.get_valid_day (not shipped to students)."""
from problem_1 import get_valid_day


def test_each_abbreviation_maps_individually(mock_input):
    # The visible suite checks the abbreviations only as one batch; pin each.
    cases = {"Mon": 1, "Tues": 2, "Weds": 3, "Thurs": 4, "Fri": 5, "Sat": 6, "Sun": 7}
    for abbrev, expected in cases.items():
        mock_input([abbrev])
        assert get_valid_day() == expected, f"{abbrev!r} should map to {expected}"


def test_mixed_case_abbreviations(mock_input):
    for abbrev, expected in {"wEdS": 3, "tUeS": 2, "sUn": 7, "fRi": 5}.items():
        mock_input([abbrev])
        assert get_valid_day() == expected, f"case-insensitive {abbrev!r} -> {expected}"


def test_full_names_lower_and_upper(mock_input):
    for name, expected in {"sunday": 7, "SATURDAY": 6, "wednesday": 3}.items():
        mock_input([name])
        assert get_valid_day() == expected


def test_recovers_after_nonalpha_then_number(mock_input):
    # invalid non-alpha ("Huh?"), invalid alpha ("Invalid day!"), then a number.
    mock_input(["@#$", "notaday", "5"])
    assert get_valid_day() == 5


def test_boundary_numbers(mock_input):
    # 7 is valid (Sunday); 8 and 0 invalid then a valid value follows.
    mock_input(["7"])
    assert get_valid_day() == 7
    mock_input(["0", "8", "1"])
    assert get_valid_day() == 1
