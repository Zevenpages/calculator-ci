Feature: Calculator web interface

  Scenario: Home page shows the form
    When I request the home page
    Then the response contains "<form"

  Scenario: Multiplication returns the result
    When I post operands 6 and 7 with operation "multiply"
    Then the response contains "42.0"

  Scenario: Division by zero shows an error
    When I post operands 5 and 0 with operation "divide"
    Then the response contains "No se puede dividir por cero"

  Scenario: Non-numeric input shows a validation error
    When I post operands x and 2 with operation "add"
    Then the response contains "Entrada invalida"

  Scenario: Comma decimal is accepted
    When I post operands 1,5 and 2,5 with operation "multiply"
    Then the response contains "3.75"

  Scenario: Multiple separators are rejected
    When I post operands 1.1.1 and 2 with operation "add"
    Then the response contains "Entrada invalida"
