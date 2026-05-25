import pytest

from app import numbers


def test_parses_plain_integer():
    assert numbers.parse_number("42") == 42.0


def test_parses_dot_decimal():
    assert numbers.parse_number("1.5") == 1.5


def test_parses_comma_decimal():
    assert numbers.parse_number("1,5") == 1.5


def test_parses_negative():
    assert numbers.parse_number("-2,5") == -2.5


def test_strips_whitespace():
    assert numbers.parse_number("  3,0  ") == 3.0


@pytest.mark.parametrize("bad", ["1.1.1", "1,1,1", "1.5,5", "1,5.5"])
def test_rejects_multiple_separators(bad):
    with pytest.raises(ValueError):
        numbers.parse_number(bad)


@pytest.mark.parametrize("bad", ["", "   ", "abc", "1,2,", "."])
def test_rejects_invalid(bad):
    with pytest.raises(ValueError):
        numbers.parse_number(bad)
