"""
test_parametrized.py
--------------------
Data-driven tests using pytest.mark.parametrize with the static datasets
defined in test_data.py.  These complement the scenario-based tests in
test_basic_operations.py with broad coverage through parametrization.
"""

import allure
import pytest

from tests.test_data import (
    ADDITION_DATA,
    DIVISION_DATA,
    EDGE_CASE_EXPRESSIONS,
    MULTIPLICATION_DATA,
    SUBTRACTION_DATA,
)


@allure.epic("Calculator Automation")
@allure.feature("Parametrized Data-Driven Tests")
class TestParametrized:

    # ── Addition ──────────────────────────────────────────────────────────────

    @allure.story("Addition")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "left, right, expected, desc",
        ADDITION_DATA,
        ids=[d[3] for d in ADDITION_DATA],
    )
    def test_addition(self, calculator, left, right, expected, desc):
        allure.dynamic.title(f"Addition: {desc}")
        result = calculator.calculate(f"{left} + {right}")
        assert result == expected, f"{left} + {right}: expected {expected!r}, got {result!r}"

    # ── Subtraction ───────────────────────────────────────────────────────────

    @allure.story("Subtraction")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "left, right, expected, desc",
        SUBTRACTION_DATA,
        ids=[d[3] for d in SUBTRACTION_DATA],
    )
    def test_subtraction(self, calculator, left, right, expected, desc):
        allure.dynamic.title(f"Subtraction: {desc}")
        result = calculator.calculate(f"{left} - {right}")
        assert result == expected, f"{left} - {right}: expected {expected!r}, got {result!r}"

    # ── Multiplication ────────────────────────────────────────────────────────

    @allure.story("Multiplication")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "left, right, expected, desc",
        MULTIPLICATION_DATA,
        ids=[d[3] for d in MULTIPLICATION_DATA],
    )
    def test_multiplication(self, calculator, left, right, expected, desc):
        allure.dynamic.title(f"Multiplication: {desc}")
        result = calculator.calculate(f"{left} * {right}")
        assert result == expected, f"{left} * {right}: expected {expected!r}, got {result!r}"

    # ── Division ──────────────────────────────────────────────────────────────

    @allure.story("Division")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "left, right, expected, desc",
        DIVISION_DATA,
        ids=[d[3] for d in DIVISION_DATA],
    )
    def test_division(self, calculator, left, right, expected, desc):
        allure.dynamic.title(f"Division: {desc}")
        result = calculator.calculate(f"{left} / {right}")
        assert result == expected, f"{left} / {right}: expected {expected!r}, got {result!r}"

    # ── Edge cases ────────────────────────────────────────────────────────────

    @allure.story("Edge Cases")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.edge_case
    @pytest.mark.parametrize(
        "expression, expected_fragment, desc",
        EDGE_CASE_EXPRESSIONS,
        ids=[d[2] for d in EDGE_CASE_EXPRESSIONS],
    )
    def test_edge_cases(self, calculator, expression, expected_fragment, desc):
        allure.dynamic.title(f"Edge case: {desc}")
        result = calculator.calculate(expression)
        assert expected_fragment in result, (
            f"[{desc}] {expression!r}: expected fragment {expected_fragment!r} in {result!r}"
        )
