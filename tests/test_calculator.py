import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from app import calculator

# Bind all scenarios in the feature file
scenarios("features/calculator.feature")


@pytest.fixture
def context():
    return {}


@given(parsers.parse("the operands {a:d} and {b:d}"), target_fixture="context")
def given_operands(a, b):
    return {"a": a, "b": b}


@when(parsers.parse('I apply the operation "{op}"'))
def apply_operation(context, op):
    func = getattr(calculator, op)
    try:
        context["result"] = func(context["a"], context["b"])
    except Exception as exc:  # noqa: BLE001 - we assert on it later
        context["error"] = exc


@then(parsers.parse("the result is {expected:d}"))
def check_result(context, expected):
    assert context["result"] == expected


@then("it raises an error")
def check_error(context):
    assert isinstance(context.get("error"), ValueError)


# Direct unit tests on the pure logic
def test_add():
    assert calculator.add(2, 3) == 5


def test_subtract():
    assert calculator.subtract(10, 4) == 6


def test_multiply():
    assert calculator.multiply(6, 7) == 42


def test_divide():
    assert calculator.divide(20, 5) == 4


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        calculator.divide(5, 0)
