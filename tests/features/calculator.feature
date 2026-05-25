Feature: Calculator operations

  Scenario: Add two numbers
    Given the operands 2 and 3
    When I apply the operation "add"
    Then the result is 5

  Scenario: Subtract two numbers
    Given the operands 10 and 4
    When I apply the operation "subtract"
    Then the result is 6

  Scenario: Multiply two numbers
    Given the operands 6 and 7
    When I apply the operation "multiply"
    Then the result is 42

  Scenario: Divide two numbers
    Given the operands 20 and 5
    When I apply the operation "divide"
    Then the result is 4

  Scenario: Divide by zero raises an error
    Given the operands 5 and 0
    When I apply the operation "divide"
    Then it raises an error
