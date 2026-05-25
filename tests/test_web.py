import pytest
from pytest_bdd import scenarios, when, then, parsers

from web.app import app as flask_app

# Bind all scenarios in the web feature file
scenarios("features/web.feature")


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    return flask_app.test_client()


@when("I request the home page", target_fixture="response")
def get_home(client):
    return client.get("/")


@when(
    parsers.parse('I post operands {a} and {b} with operation "{op}"'),
    target_fixture="response",
)
def post_operation(client, a, b, op):
    return client.post("/", data={"a": a, "b": b, "operation": op})


@then(parsers.parse('the response contains "{text}"'))
def response_contains(response, text):
    assert response.status_code == 200
    assert text in response.get_data(as_text=True)
