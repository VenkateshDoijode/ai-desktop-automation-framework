"""
test_basic_operations.py
------------------------
Tests for the four fundamental arithmetic operations in Standard mode.
All tests use the CalculatorPage POM and produce rich Allure output.
"""

import allure
import pytest

from utils.screenshot_helper import capture_and_attach


@allure.epic("Calculator Automation")
@allure.feature("Standard Mode – Basic Operations")
class TestBasicOperations:

    # ------------------------------------------------------------------
    # Addition
    # ------------------------------------------------------------------

    @allure.story("Addition")
    @allure.title("Add two positive integers")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_add_positive_integers(self, calculator):
        result = calculator.calculate("5 + 3")
        assert result == "8", f"Expected 8, got {result}"

    @allure.story("Addition")
    @allure.title("Add zero to a number")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_add_zero(self, calculator):
        result = calculator.calculate("42 + 0")
        assert result == "42"

    @allure.story("Addition")
    @allure.title("Add two large numbers")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_add_large_numbers(self, calculator):
        result = calculator.calculate("999999 + 1")
        assert result == "1,000,000"

    @allure.story("Addition")
    @allure.title("Add negative numbers")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_add_negative(self, calculator):
        result = calculator.calculate("-5 + -3")
        assert result == "-8"

    # ------------------------------------------------------------------
    # Subtraction
    # ------------------------------------------------------------------

    @allure.story("Subtraction")
    @allure.title("Subtract two positive integers")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_subtract_positive(self, calculator):
        result = calculator.calculate("10 - 3")
        assert result == "7"

    @allure.story("Subtraction")
    @allure.title("Subtract resulting in negative")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_subtract_negative_result(self, calculator):
        result = calculator.calculate("3 - 10")
        assert result == "-7"

    @allure.story("Subtraction")
    @allure.title("Subtract zero from number")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_subtract_zero(self, calculator):
        result = calculator.calculate("55 - 0")
        assert result == "55"

    # ------------------------------------------------------------------
    # Multiplication
    # ------------------------------------------------------------------

    @allure.story("Multiplication")
    @allure.title("Multiply two positive integers")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_multiply_positive(self, calculator):
        result = calculator.calculate("6 * 7")
        assert result == "42"

    @allure.story("Multiplication")
    @allure.title("Multiply by zero")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edge_case
    def test_multiply_by_zero(self, calculator):
        result = calculator.calculate("12345 * 0")
        assert result == "0"

    @allure.story("Multiplication")
    @allure.title("Multiply by one (identity)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_multiply_by_one(self, calculator):
        result = calculator.calculate("99 * 1")
        assert result == "99"

    @allure.story("Multiplication")
    @allure.title("Multiply two negative numbers")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_multiply_negatives(self, calculator):
        result = calculator.calculate("-4 * -3")
        assert result == "12"

    # ------------------------------------------------------------------
    # Division
    # ------------------------------------------------------------------

    @allure.story("Division")
    @allure.title("Divide two integers evenly")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_divide_evenly(self, calculator):
        result = calculator.calculate("20 / 4")
        assert result == "5"

    @allure.story("Division")
    @allure.title("Divide resulting in decimal")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_divide_decimal_result(self, calculator):
        result = calculator.calculate("1 / 3")
        assert "0.3333" in result, f"Expected a repeating decimal, got {result}"

    @allure.story("Division")
    @allure.title("Divide by zero returns error")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.edge_case
    def test_divide_by_zero(self, calculator):
        result = calculator.calculate("5 / 0")
        assert "Cannot divide by zero" in result or "∞" in result or "Infinity" in result, \
            f"Expected divide-by-zero message, got {result!r}"

    @allure.story("Division")
    @allure.title("Divide zero by a number")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_divide_zero_by_number(self, calculator):
        result = calculator.calculate("0 / 5")
        assert result == "0"

    # ------------------------------------------------------------------
    # UI Controls
    # ------------------------------------------------------------------

    @allure.story("UI Controls")
    @allure.title("Clear button resets display to zero")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_clear_button(self, calculator):
        calculator.enter_number(12345)
        calculator.clear()
        result = calculator.get_display()
        assert result == "0", f"Expected 0 after clear, got {result}"

    @allure.story("UI Controls")
    @allure.title("Backspace removes last digit")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_backspace(self, calculator):
        calculator.clear()
        calculator.enter_number(123)
        calculator.press_key("⌫")
        result = calculator.get_display()
        assert result == "12", f"Expected 12 after backspace on 123, got {result}"

    @allure.story("UI Controls")
    @allure.title("Consecutive operations chain correctly")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_consecutive_operations(self, calculator):
        # 10 + 5 = 15, then 15 - 3 = 12
        calculator.clear()
        calculator.enter_number(10)
        calculator.press_operator("+")
        calculator.enter_number(5)
        calculator.press_equals()
        calculator.press_operator("-")
        calculator.enter_number(3)
        calculator.press_equals()
        assert calculator.get_display() == "12"
